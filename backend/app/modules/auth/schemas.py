"""
app/modules/auth/schemas.py
"""
from app.shared.utils.phone import normalize_phone
from uuid import UUID
from pydantic import EmailStr, Field, field_validator, model_validator
from app.shared.schemas.base import BaseSchema
from app.modules.users.models import UserRole


class RegisterRequest(BaseSchema):
    """Inscription simplifiée : nom, téléphone, mot de passe. Email facultatif.
    Avec center_join_token + branch_id : inscription via le lien d'un centre,
    en attente de validation par la secrétaire."""
    full_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(max_length=20)
    password: str = Field(min_length=6, max_length=100)
    email: EmailStr | None = None
    referral_code: str | None = None
    whatsapp_opt_in: bool = False
    center_join_token: str | None = Field(default=None, max_length=64)
    branch_id: UUID | None = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_is_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str) -> str:
        normalized = normalize_phone(v)
        if not normalized:
            raise ValueError("Indiquez votre numéro de téléphone.")
        return normalized

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def join_needs_branch(self):
        if self.center_join_token and not self.branch_id:
            raise ValueError("Choisissez votre succursale.")
        return self


class LoginRequest(BaseSchema):
    """Connexion par numéro de téléphone (ou email, pour les comptes existants)."""
    identifier: str | None = Field(
        default=None, max_length=255, description="Numéro de téléphone ou email"
    )
    # Ancien champ, accepté pour compatibilité
    email: str | None = Field(default=None, max_length=255)
    password: str
    device_fingerprint: str | None = Field(
        default=None,
        max_length=255,
        description="Identifiant stable de l'appareil, généré côté client (ex: FingerprintJS ou UUID stocké localement).",
    )

    @model_validator(mode="after")
    def needs_identifier(self):
        if not (self.identifier or self.email or "").strip():
            raise ValueError("Indiquez votre numéro de téléphone.")
        return self

    @property
    def login_id(self) -> str:
        return (self.identifier or self.email or "").strip()


class LogoutRequest(BaseSchema):
    device_fingerprint: str | None = None
    
class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class AuthUserResponse(BaseSchema):
    """Infos user retournées dans la response auth."""
    id: UUID
    email: str
    full_name: str
    phone: str | None = None
    is_admin: bool
    is_verified: bool
    is_ambassador: bool
    role: UserRole
    center_id: UUID | None = None
    branch_id: UUID | None = None
    requested_branch_id: UUID | None = None


class AuthResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class RefreshTokenRequest(BaseSchema):
    refresh_token: str