"""
app/modules/auth/schemas.py
"""
from uuid import UUID
from pydantic import EmailStr, Field
from app.shared.schemas.base import BaseSchema


class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


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


class AuthResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class RefreshTokenRequest(BaseSchema):
    refresh_token: str