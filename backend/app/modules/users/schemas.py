"""
app/modules/users/schemas.py
"""
import uuid
from datetime import datetime
from pydantic import EmailStr, Field, field_validator
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Requests
# ─────────────────────────────────────────────

class UserRegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule.")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str) -> str:
        return v.strip()


class UserUpdateRequest(BaseSchema):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str | None) -> str | None:
        return v.strip() if v else None


class UserChangePasswordRequest(BaseSchema):
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule.")
        return v


class PasswordResetRequestSchema(BaseSchema):
    """Demande d'envoi du lien de reset."""
    email: EmailStr


class PasswordResetConfirmSchema(BaseSchema):
    """Confirmation du reset avec le token reçu par email."""
    token: str
    new_password: str = Field(min_length=8, max_length=100)


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────

class UserResponse(BaseSchema):
    """Réponse publique — pas de données sensibles."""
    id: uuid.UUID
    email: str
    full_name: str
    phone: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime


class UserAdminResponse(UserResponse):
    """Réponse étendue pour l'admin."""
    is_admin: bool
    updated_at: datetime


class UserMeResponse(UserResponse):
    """Réponse pour /users/me — idem public pour l'instant."""
    pass