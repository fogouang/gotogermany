"""
app/modules/users/schemas.py
"""
import uuid
from datetime import datetime
from pydantic import EmailStr, Field, field_validator
from app.shared.schemas.base import BaseSchema
from app.modules.users.models import UserRole


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


# ── Licence de centre ────────────────────────

class DirectorCreateRequest(BaseSchema):
    """Création d'un compte center_director — admin ITIA uniquement."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    center_id: uuid.UUID

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str) -> str:
        return v.strip()


class SecretaryCreateRequest(BaseSchema):
    """Création d'un compte branch_secretary — par le directeur de centre."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    branch_id: uuid.UUID

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str) -> str:
        return v.strip()


class StudentCreateRequest(BaseSchema):
    """Création d'un compte student rattaché à un centre — par la secrétaire."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    target_level_id: uuid.UUID
    access_duration_days: int | None = Field(default=None, gt=0, le=365)

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str) -> str:
        return v.strip()


class StudentTargetUpdateRequest(BaseSchema):
    """Modification du level ciblé — par la secrétaire, sans consommer le quota."""
    target_level_id: uuid.UUID


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
    ai_credits: int = 0
    role: UserRole


class UserAdminResponse(UserResponse):
    """Réponse étendue pour l'admin."""
    is_admin: bool
    updated_at: datetime
    center_id: uuid.UUID | None
    branch_id: uuid.UUID | None


class UserMeResponse(UserResponse):
    """Réponse pour /users/me — inclut le contexte centre/branch si applicable."""
    center_id: uuid.UUID | None
    branch_id: uuid.UUID | None
    target_level_id: uuid.UUID | None
    access_expires_at: datetime | None


class StudentResponse(BaseSchema):
    """Réponse pour la liste des étudiants d'une succursale (vue secrétaire/directeur)."""
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    target_level_id: uuid.UUID | None
    first_login_at: datetime | None
    access_expires_at: datetime | None
    created_at: datetime
    ai_credits: int = 0 
    

class StudentCreditAdjustRequest(BaseSchema):
    """Secrétaire ou directeur rechargent un étudiant précis — prélevé du pool du centre."""
    amount: int = Field(gt=0, le=100)
    reason: str | None = Field(default=None, max_length=255)


class StudentAccessDatesUpdateRequest(BaseSchema):
    """Directeur ajuste la fenêtre d'accès d'un étudiant précis."""
    access_expires_at: datetime | None = None
    access_duration_days: int | None = Field(default=None, gt=0, le=365)


class StudentProgressResponse(BaseSchema):
    """Une ligne de la vue 'évolution des étudiants' — secrétaire (sa branche) ou directeur (tout le centre)."""
    student_id: uuid.UUID
    student_name: str
    branch_name: str
    total_sessions: int
    average_score: float | None
    last_session_at: datetime | None
    ai_credits_remaining: int
    

class ModuleScoreBreakdown(BaseSchema):
    """Score moyen pour un module donné (Lesen, Hören, Schreiben, Sprechen...)."""
    module_name: str
    average_score: float | None


class ExamProgressResponse(BaseSchema):
    """Progression détaillée sur un examen précis (ex: Goethe-Zertifikat B2)."""
    exam_id: uuid.UUID
    exam_name: str
    total_sessions: int
    average_score: float | None
    last_session_at: datetime | None
    modules: list[ModuleScoreBreakdown]


class ScoreHistoryPoint(BaseSchema):
    """Un point pour le graphique d'évolution des scores dans le temps."""
    date: datetime
    score: float
    exam_name: str


class StudentDetailedProgressResponse(BaseSchema):
    """Vue détaillée d'un étudiant — ventilation par examen/module + historique pour graphes."""
    student_id: uuid.UUID
    student_name: str
    branch_name: str
    ai_credits_remaining: int
    total_sessions: int
    overall_average_score: float | None
    last_session_at: datetime | None
    exams: list[ExamProgressResponse]
    score_history: list[ScoreHistoryPoint]