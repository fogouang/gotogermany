"""
app/modules/auth/schemas.py
"""
from uuid import UUID
from pydantic import EmailStr, Field
from app.shared.schemas.base import BaseSchema
from app.modules.users.models import UserRole


class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    referral_code: str | None = None


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str
    device_fingerprint: str | None = Field(
        default=None,
        max_length=255,
        description="Identifiant stable de l'appareil, généré côté client (ex: FingerprintJS ou UUID stocké localement).",
    )


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class AuthUserResponse(BaseSchema):
    """Infos user retournées dans la response auth."""
    id: UUID
    email: str
    full_name: str
    is_admin: bool
    is_verified: bool
    is_ambassador: bool
    role: UserRole
    center_id: UUID | None = None
    branch_id: UUID | None = None


class AuthResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class RefreshTokenRequest(BaseSchema):
    refresh_token: str