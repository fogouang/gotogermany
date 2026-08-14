"""
app/modules/auth/router.py
"""
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RegisterRequest,
)
from app.modules.auth.service import AuthService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse
from app.shared.dependencies import CurrentUser

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Inscription d'un nouvel utilisateur."""
    return await AuthService(db).register(data)


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Connexion — retourne un JWT."""
    return await AuthService(db).login(data)

@router.post("/logout", response_model=SuccessResponse)
async def logout(
    data: LogoutRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Libère le slot d'appareil du fingerprint fourni."""
    await AuthService(db).logout(current_user.id, data.device_fingerprint)
    return SuccessResponse(message="Déconnexion réussie.")

@router.post("/verify-email/{token}", response_model=SuccessResponse)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Vérification de l'adresse email via le token reçu par email."""
    await AuthService(db).verify_email(token)
    return SuccessResponse(message="Email vérifié avec succès.")


@router.post("/password-reset/request", response_model=SuccessResponse)
async def request_password_reset(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """Demande de réinitialisation du mot de passe."""
    await AuthService(db).request_password_reset(email)
    # Toujours retourner 200 pour ne pas révéler si l'email existe
    return SuccessResponse(message="Si cet email existe, un lien de réinitialisation a été envoyé.")


@router.post("/password-reset/confirm", response_model=SuccessResponse)
async def confirm_password_reset(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
):
    """Confirmation du reset avec le token et le nouveau mot de passe."""
    await AuthService(db).confirm_password_reset(token, new_password)
    return SuccessResponse(message="Mot de passe réinitialisé avec succès.")