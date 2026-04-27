"""
app/modules/auth/service.py
"""
import secrets
from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas import AuthResponse, AuthUserResponse, LoginRequest, RegisterRequest
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.shared.exceptions.http import BadRequestException, UnauthorizedException
from app.shared.security.jwt import create_access_token, decode_access_token
from app.shared.security.password import hash_password, verify_password


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> AuthResponse:
        # Email unique
        existing = await self.repo.find_by_email(data.email)
        if existing:
            raise BadRequestException(detail="Cet email est déjà utilisé.")

        # Créer l'utilisateur
        verification_token = secrets.token_urlsafe(32)
        user = await self.repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name.strip(),
            phone=data.phone,
            is_active=True,
            is_admin=False,
            is_verified=False,
            verification_token=verification_token,
        )

        # TODO: envoyer email de vérification avec verification_token

        access_token = create_access_token({"sub": str(user.id)})
        return AuthResponse(
            access_token=access_token,
            user=AuthUserResponse.model_validate(user),
        )

    async def login(self, data: LoginRequest) -> AuthResponse:
        user = await self.repo.find_by_email(data.email)

        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException(detail="Email ou mot de passe incorrect.")

        if not user.is_active:
            raise UnauthorizedException(detail="Compte désactivé.")

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