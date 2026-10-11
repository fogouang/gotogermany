"""
app/modules/assignments/schemas.py
"""
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from app.modules.exam_sessions.schemas import SessionResultResponse
from app.shared.schemas.base import BaseSchema


class BankSubjectResponse(BaseSchema):
    subject_id: uuid.UUID
    subject_name: str
    subject_number: int
    exam_id: uuid.UUID
    exam_name: str
    provider: str
    level_id: uuid.UUID
    cefr_code: str
    modules: list[str] = []


class AssignmentCreate(BaseSchema):
    subject_id: uuid.UUID
    title: str = Field(min_length=2, max_length=150)
    instructions: str | None = Field(default=None, max_length=2000)
    due_at: datetime | None = None
    class_ids: list[uuid.UUID] = []
    student_ids: list[uuid.UUID] = []

    @model_validator(mode="after")
    def at_least_one_target(self):
        if not self.class_ids and not self.student_ids:
            raise ValueError("Choisissez au moins une classe ou un élève.")
        return self


class AssignmentTargetResponse(BaseSchema):
    type: Literal["class", "student"]
    id: uuid.UUID
    name: str


class AssignmentSummaryResponse(BaseSchema):
    id: uuid.UUID
    title: str
    instructions: str | None
    subject_id: uuid.UUID
    subject_name: str
    exam_name: str
    cefr_code: str
    due_at: datetime | None
    is_cancelled: bool
    created_at: datetime
    targets: list[AssignmentTargetResponse] = []
    expected_count: int = 0
    submitted_count: int = 0
    graded_count: int = 0


class SubmissionRowResponse(BaseSchema):
    student_id: uuid.UUID
    student_name: str
    status: str                      # pending | in_progress | submitted | graded
    exam_session_id: uuid.UUID | None
    started_at: datetime | None
    submitted_at: datetime | None
    graded_at: datetime | None
    is_late: bool
    score_breakdown: dict[str, Any] | None
    final_score: float | None
    has_annotated_file: bool


class AssignmentDetailResponse(AssignmentSummaryResponse):
    submissions: list[SubmissionRowResponse] = []


class StudentAssignmentResponse(BaseSchema):
    """Vue élève : uniquement la note finale, jamais le détail."""
    id: uuid.UUID
    title: str
    instructions: str | None
    exam_name: str
    cefr_code: str
    teacher_name: str
    due_at: datetime | None
    is_late: bool
    status: str
    final_score: float | None


class GradeAnswer(BaseSchema):
    question_id: uuid.UUID
    score: float = Field(ge=0)
    # Détail facultatif par critère, ex. {"Erfüllung": 18, "Kohärenz": 20}
    criteria: dict[str, float] | None = None
    comment: str | None = Field(default=None, max_length=2000)


class GradeRequest(BaseSchema):
    answers: list[GradeAnswer] = Field(min_length=1)
    teacher_comment: str | None = Field(default=None, max_length=4000)


class SubmissionGradingResponse(BaseSchema):
    submission: SubmissionRowResponse
    teacher_comment: str | None
    # Résultat complet (réponses, textes, audios, corrigés) : vue enseignant uniquement
    result: SessionResultResponse | None