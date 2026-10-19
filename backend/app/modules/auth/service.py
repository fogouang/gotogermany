"""
app/modules/auth/service.py
"""
import secrets
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas import AuthResponse, AuthUserResponse, LoginRequest, RegisterRequest
from app.modules.users.models import User
from app.modules.users.repository import UserRepository, UserDeviceRepository
from app.shared.exceptions.http import BadRequestException, UnauthorizedException
from app.shared.security.jwt import create_access_token, decode_access_token
from app.shared.security.password import hash_password, verify_password
from app.shared.utils.phone import normalize_phone
from app.modules.referrals.service import ReferralService

# Adresse interne des comptes créés sans email (même domaine que la création rapide)
PLACEHOLDER_EMAIL_DOMAIN = "@internal.gotogermany"


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.device_repo = UserDeviceRepository(db)
        self.referral_service = ReferralService(db)

    async def register(self, data: RegisterRequest) -> AuthResponse:
        # Email unique, seulement s'il est fourni
        if data.email:
            existing = await self.repo.find_by_email(data.email)
            if existing:
                raise BadRequestException(detail="Cet email est déjà utilisé.")

        # Un numéro = un compte (le numéro sert à se connecter)
        if await self.repo.find_by_phone(data.phone):
            raise BadRequestException(
                detail="Ce numéro est déjà utilisé. Connectez-vous avec ce numéro."
            )

        # Inscription via le lien d'un centre : demande en attente de validation
        requested_branch_id = None
        if data.center_join_token:
            from app.modules.centers.service import CenterService

            branch = await CenterService(self.db).resolve_join_branch(
                data.center_join_token, data.branch_id
            )
            requested_branch_id = branch.id

        # Résolution du parrainage (silencieuse si code invalide/inexistant)
        referred_by_user_id = None
        if data.referral_code:
            ambassador = await self.referral_service.resolve_referrer(data.referral_code)
            if ambassador:
                referred_by_user_id = ambassador.id

        now = datetime.now(timezone.utc)
        extra: dict = {}
        if requested_branch_id:
            # Pas de crédits offerts : ceux du centre arrivent à la validation
            extra.update(
                requested_branch_id=requested_branch_id,
                join_requested_at=now,
                ai_credits=0,
            )

        verification_token = secrets.token_urlsafe(32)
        user = await self.repo.create(
            email=data.email or f"compte-{uuid4().hex[:12]}{PLACEHOLDER_EMAIL_DOMAIN}",
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            whatsapp_opt_in=data.whatsapp_opt_in,
            whatsapp_opt_in_at=now if data.whatsapp_opt_in else None,
            is_active=True,
            is_admin=False,
            is_verified=False,
            verification_token=verification_token,
            referred_by_user_id=referred_by_user_id,
            **extra,
        )

        # TODO: envoyer email de vérification avec verification_token (si email fourni)

        access_token = create_access_token({"sub": str(user.id)})
        return AuthResponse(
            access_token=access_token,
            user=AuthUserResponse.model_validate(user),
        )

    async def _find_by_identifier(self, identifier: str) -> User | None:
        """Email si l'identifiant contient un @, sinon numéro de téléphone
        (normalisé : "6 90 00 00 00" et "+237690000000" donnent le même compte)."""
        if "@" in identifier:
            return await self.repo.find_by_email(identifier)
        try:
            phone = normalize_phone(identifier)
        except ValueError:
            return None
        return await self.repo.find_by_phone(phone) if phone else None
        
    async def login(self, data: LoginRequest) -> AuthResponse:
        user = await self._find_by_identifier(data.login_id)

        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException(detail="Numéro ou mot de passe incorrect.")

        if not user.is_active:
            raise UnauthorizedException(detail="Compte désactivé.")

        # Centre désactivé (admin ITIA) — bloque tout le personnel/étudiants
        # rattachés, que ce soit via center_id direct (directeur) ou via
        # branch_id -> Branch.center_id (secrétaire, enseignant, étudiant).
        center_id_to_check = user.center_id
        if center_id_to_check is None and user.branch_id is not None:
            from app.modules.centers.repository import BranchRepository
            branch = await BranchRepository(self.db).get_by_id_or_404(user.branch_id)
            center_id_to_check = branch.center_id

        if center_id_to_check is not None:
            from app.modules.centers.repository import CenterRepository
            center = await CenterRepository(self.db).get_by_id_or_404(center_id_to_check)
            if not center.is_active:
                raise UnauthorizedException(detail="Ce centre est actuellement désactivé.")

        # Gestion des appareils — max 5 par compte (libéré au logout)
        if data.device_fingerprint:
            await self.device_repo.register_device_or_raise(
                user_id=user.id,
                fingerprint=data.device_fingerprint,
            )

        access_token = create_access_token({"sub": str(user.id)})
        return AuthResponse(
            access_token=access_token,
            user=AuthUserResponse.model_validate(user),
        )
        
        
    async def get_current_user(self, token: str) -> User:
        payload = decode_access_token(token)
        if payload is None:
            raise UnauthorizedException(detail="Token invalide ou expiré.")

        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException(detail="Token invalide.")

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise UnauthorizedException(detail="Token invalide.")

        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException(detail="Utilisateur introuvable.")
        if not user.is_active:
            raise UnauthorizedException(detail="Compte désactivé.")

        # Centre désactivé (admin ITIA) — coupe l'accès immédiatement, même
        # pour une session déjà ouverte avec un token encore valide. Couvre
        # center_id direct (directeur) et branch_id -> Branch.center_id
        # (secrétaire, enseignant, étudiant). Un B2C individuel (les deux
        # None) n'est jamais concerné.
        center_id_to_check = user.center_id
        if center_id_to_check is None and user.branch_id is not None:
            from app.modules.centers.repository import BranchRepository
            branch = await BranchRepository(self.db).get_by_id_or_404(user.branch_id)
            center_id_to_check = branch.center_id

        if center_id_to_check is not None:
            from app.modules.centers.repository import CenterRepository
            center = await CenterRepository(self.db).get_by_id_or_404(center_id_to_check)
            if not center.is_active:
                raise UnauthorizedException(detail="Ce centre est actuellement désactivé.")

        return user

    async def verify_email(self, token: str) -> User:
        user = await self.repo.find_by_verification_token(token)
        if not user:
            raise BadRequestException(detail="Token de vérification invalide.")

        return await self.repo.update(
            user.id,
            is_verified=True,
            verification_token=None,
        )

    async def request_password_reset(self, email: str) -> str:
        """Génère un reset token. Retourne le token pour l'envoyer par email."""
        user = await self.repo.find_by_email(email)
        # On ne révèle pas si l'email existe ou non
        if not user:
            return ""

        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        await self.repo.update(
            user.id,
            reset_token=reset_token,
            reset_token_expires_at=expires_at,
        )
        # TODO: envoyer email avec reset_token
        return reset_token

    async def confirm_password_reset(self, token: str, new_password: str) -> User:
        user = await self.repo.find_by_reset_token(token)
        if not user:
            raise BadRequestException(detail="Token invalide ou expiré.")

        if user.reset_token_expires_at and user.reset_token_expires_at < datetime.now(timezone.utc):
            raise BadRequestException(detail="Token expiré.")

        return await self.repo.update(
            user.id,
            hashed_password=hash_password(new_password),
            reset_token=None,
            reset_token_expires_at=None,
        )
        
    async def logout(self, user_id: UUID, device_fingerprint: str | None) -> None:
        """Libère le slot d'appareil correspondant au fingerprint fourni.
        Idempotent — pas d'erreur si le fingerprint n'était déjà plus
        enregistré (ex. double-clic, ou déjà retiré via /me/devices)."""
        if device_fingerprint:
            await self.device_repo.remove_device(user_id, device_fingerprint)