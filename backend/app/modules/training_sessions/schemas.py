"""
app/modules/training_sessions/schemas.py
"""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from app.shared.schemas.base import BaseSchema

# Niveau d'une classe Start Deutsch
StartDeutschLevel = Literal["A1", "A2"]
# Parcours de la classe : examens B1/B2 ou Start Deutsch A1/A2
ClassTrack = Literal["exam", "start_deutsch"]


class TrainingSessionCreateRequest(BaseSchema):
    branch_id: uuid.UUID | None = Field(
        default=None,
        description="Requis pour un directeur (plusieurs branches possibles). "
                    "Ignoré pour une secrétaire (sa propre branche s'applique).",
    )
    # Un seul des deux : niveau du catalogue des examens, ou niveau Start Deutsch
    level_id: uuid.UUID | None = None
    sd_level: StartDeutschLevel | None = None
    label: str | None = Field(default=None, max_length=150)
    start_date: datetime
    end_date: datetime | None = None
    # Création en une étape : enseignants et élèves affectés directement
    teacher_ids: list[uuid.UUID] = []
    student_ids: list[uuid.UUID] = []

    @model_validator(mode="after")
    def one_level(self):
        if (self.level_id is None) == (self.sd_level is None):
            raise ValueError("Choisissez un niveau d'examen ou un niveau Start Deutsch (A1, A2).")
        return self


class TrainingSessionUpdateRequest(BaseSchema):
    label: str | None = Field(default=None, max_length=150)
    end_date: datetime | None = None


class TeacherAssignRequest(BaseSchema):
    teacher_id: uuid.UUID


class StudentEnrollRequest(BaseSchema):
    student_id: uuid.UUID


class StudentEndRequest(BaseSchema):
    ended_at: datetime | None = Field(
        default=None, description="Si omis, utilise la date/heure actuelle."
    )


class TrainingSessionStudentResponse(BaseSchema):
    student_id: uuid.UUID
    student_name: str
    enrolled_at: datetime
    ended_at: datetime | None


class TrainingSessionTeacherResponse(BaseSchema):
    teacher_id: uuid.UUID
    teacher_name: str


class TrainingSessionResponse(BaseSchema):
    id: uuid.UUID
    branch_id: uuid.UUID
    branch_name: str
    track: ClassTrack = "exam"
    level_id: uuid.UUID | None          # absent pour une classe Start Deutsch
    sd_level: StartDeutschLevel | None = None
    cefr_code: str = ""                 # B1, B2, A1, A2 : pour afficher et filtrer
    level_name: str
    label: str | None
    start_date: datetime
    end_date: datetime | None
    created_at: datetime
    # Brouillon = aucun élève actif : la classe est masquée aux enseignants
    is_draft: bool = False
    teachers: list[TrainingSessionTeacherResponse] = []
    students: list[TrainingSessionStudentResponse] = []


class TrainingSessionStatsResponse(BaseSchema):
    total_started: int
    total_ended: int
    total_active: int


class TeacherCommentCreateRequest(BaseSchema):
    comment: str = Field(min_length=1, max_length=2000)


class TeacherCommentResponse(BaseSchema):
    id: uuid.UUID
    teacher_id: uuid.UUID
    teacher_name: str
    comment: str
    created_at: datetime