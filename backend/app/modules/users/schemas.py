"""
app/modules/users/schemas.py
"""
from app.shared.utils.phone import normalize_phone
import uuid
from datetime import datetime
from typing import Literal
from pydantic import EmailStr, Field, field_validator, model_validator
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
    
    # Niveau actif de l'étudiant individuel (préférence d'affichage).
    # Ignoré/refusé pour un élève de centre : c'est le centre qui fixe son niveau.
    target_level_id: uuid.UUID | None = None
    whatsapp_opt_in: bool | None = None
    # Parcours choisi à l'accueil (étudiant individuel uniquement)
    learning_track: Literal["exam", "start_deutsch"] | None = None
        
    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str | None) -> str | None:
        return v.strip() if v else None

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str | None) -> str | None:
        return normalize_phone(v)
    
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
    is_ambassador: bool
    role: UserRole
    whatsapp_opt_in: bool = False
    learning_track: str | None = None


class UserAdminResponse(UserResponse):
    """Réponse étendue pour l'admin."""
    is_admin: bool
    is_ambassador: bool
    updated_at: datetime
    center_id: uuid.UUID | None
    branch_id: uuid.UUID | None
    whatsapp_opt_in_at: datetime | None = None

class UserMeResponse(UserResponse):
    """Réponse pour /users/me — inclut le contexte centre/branch si applicable."""
    is_admin: bool
    is_ambassador: bool
    center_id: uuid.UUID | None
    branch_id: uuid.UUID | None
    target_level_id: uuid.UUID | None
    # Niveau Start Deutsch ("A1", "A2") d'un élève de centre en parcours A1/A2
    target_sd_level: str | None = None
    access_expires_at: datetime | None
    # Inscription via le lien d'un centre, en attente de validation
    requested_branch_id: uuid.UUID | None = None


class StudentResponse(BaseSchema):
    """Réponse pour la liste des étudiants d'une succursale (vue secrétaire/directeur)."""
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    branch_id: uuid.UUID | None
    target_level_id: uuid.UUID | None
    target_sd_level: str | None = None
    learning_track: str | None = None
    first_login_at: datetime | None
    access_expires_at: datetime | None
    created_at: datetime
    ai_credits: int = 0
    

class StudentCreditAdjustRequest(BaseSchema):
    """Secrétaire ou directeur rechargent un étudiant précis — prélevé du pool du centre."""
    amount: int = Field(gt=0, le=100)
    reason: str | None = Field(default=None, max_length=255)



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
    questions_correct: int = 0
    questions_incorrect: int = 0
    questions_total: int = 0

class SubjectScoreBreakdown(BaseSchema):
    """Score par module (Lesen/Hören/Schreiben/Sprechen) pour un sujet précis."""
    subject_id: uuid.UUID
    subject_name: str
    total_sessions: int
    average_score: float | None
    last_session_at: datetime | None
    last_session_id: uuid.UUID | None = None
    modules: list[ModuleScoreBreakdown]
    
class ExamProgressResponse(BaseSchema):
    exam_id: uuid.UUID
    exam_name: str
    total_sessions: int
    average_score: float | None
    last_session_at: datetime | None
    subjects: list[SubjectScoreBreakdown]


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
    

class StudentQuickCreateRequest(BaseSchema):
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    branch_id: uuid.UUID | None = Field(
        default=None,
        description="Requis si créé par un directeur (plusieurs branches possibles). "
                    "Ignoré si créé par une secrétaire (sa propre branche s'applique).",
    )

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str) -> str:
        return v.strip()
    
    
class TeacherCreateRequest(BaseSchema):
    """Création d'un compte teacher — par le directeur (branch_id requis,
    plusieurs succursales possibles) ou la secrétaire (sa propre succursale
    s'applique, branch_id ignoré si fourni)."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    branch_id: uuid.UUID | None = Field(default=None)

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str) -> str:
        return v.strip()
    
# ── Inscriptions via le lien du centre ───────

class JoinRequestResponse(BaseSchema):
    id: uuid.UUID
    full_name: str
    phone: str | None
    email: str | None
    branch_id: uuid.UUID
    branch_name: str
    requested_at: datetime | None


class JoinRequestApproveRequest(BaseSchema):
    """Niveau attribué à la validation : un niveau d'examen, ou Start Deutsch A1 / A2."""
    target_level_id: uuid.UUID | None = None
    target_sd_level: Literal["A1", "A2"] | None = None

    @model_validator(mode="after")
    def one_level(self):
        if (self.target_level_id is None) == (self.target_sd_level is None):
            raise ValueError("Choisissez un niveau d'examen ou un niveau Start Deutsch (A1, A2).")
        return self