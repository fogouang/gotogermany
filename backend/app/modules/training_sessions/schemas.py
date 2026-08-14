"""
app/modules/training_sessions/schemas.py
"""
import uuid
from datetime import datetime
from pydantic import Field
from app.shared.schemas.base import BaseSchema


class TrainingSessionCreateRequest(BaseSchema):
    branch_id: uuid.UUID | None = Field(
        default=None,
        description="Requis pour un directeur (plusieurs branches possibles). "
                    "Ignoré pour une secrétaire (sa propre branche s'applique).",
    )
    level_id: uuid.UUID
    label: str | None = Field(default=None, max_length=150)
    start_date: datetime
    end_date: datetime | None = None


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
    level_id: uuid.UUID
    level_name: str
    label: str | None
    start_date: datetime
    end_date: datetime | None
    created_at: datetime
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