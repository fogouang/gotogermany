"""
app/modules/exams/schemas.py
"""
import uuid
from datetime import datetime
from typing import Any
from pydantic import Field
from app.shared.schemas.base import BaseSchema


# ─── Question (léger pour aperçu) ────────────

class QuestionLightResponse(BaseSchema):
    id: uuid.UUID
    question_number: int
    question_type: str
    points: int
    audio_file: str | None = None


# ─── Teil ────────────────────────────────────

class TeilCreateRequest(BaseSchema):
    teil_number: int = Field(gt=0)
    format_type: str = Field(max_length=50)
    instructions: str | None = None
    max_score: int = Field(gt=0)
    time_minutes: int | None = Field(default=None, gt=0)
    config: dict[str, Any] | None = None


class TeilResponse(BaseSchema):
    id: uuid.UUID
    teil_number: int
    format_type: str
    instructions: str | None
    max_score: int
    time_minutes: int | None
    config: dict[str, Any] | None


class TeilWithQuestionsResponse(TeilResponse):
    questions: list[QuestionLightResponse] = []


# ─── Module ──────────────────────────────────

class ModuleCreateRequest(BaseSchema):
    slug: str = Field(max_length=50, pattern=r"^[a-z_]+$")
    name: str = Field(max_length=100)
    time_limit_minutes: int = Field(gt=0)
    max_score: int = Field(gt=0)
    display_order: int = Field(default=0, ge=0)


class ModuleResponse(BaseSchema):
    id: uuid.UUID
    slug: str
    name: str
    time_limit_minutes: int
    max_score: int
    display_order: int


class ModuleWithTeilenResponse(ModuleResponse):
    teile: list[TeilResponse] = []


class ModuleWithQuestionsResponse(ModuleResponse):
    """Module avec teile + questions — pour aperçu admin."""
    teile: list[TeilWithQuestionsResponse] = []


# ─── Subject ─────────────────────────────────

class SubjectCreateRequest(BaseSchema):
    name: str | None = Field(default=None, max_length=100)
    is_active: bool = True


class SubjectUpdateRequest(BaseSchema):
    name: str | None = None
    is_active: bool | None = None


class SubjectResponse(BaseSchema):
    id: uuid.UUID
    level_id: uuid.UUID
    subject_number: int
    name: str | None
    is_active: bool
    has_audio: bool = False  # ← True si au moins 1 question a audio_file


class SubjectWithModulesResponse(SubjectResponse):
    """Subject avec modules + teile (sans questions) — pour page détail."""
    modules: list[ModuleWithTeilenResponse] = []


class SubjectWithQuestionsResponse(SubjectResponse):
    """Subject avec modules + teile + questions — pour aperçu admin."""
    modules: list[ModuleWithQuestionsResponse] = []


# ─── Level ───────────────────────────────────

class LevelCreateRequest(BaseSchema):
    cefr_code: str = Field(max_length=10)
    total_pass_score: int = Field(gt=0)
    scoring_notes: str | None = None
    display_order: int = Field(default=0, ge=0)
    is_free: bool = False
    exam_config: dict[str, Any] | None = None


class LevelUpdateRequest(BaseSchema):
    total_pass_score: int | None = Field(default=None, gt=0)
    scoring_notes: str | None = None
    display_order: int | None = Field(default=None, ge=0)
    is_free: bool | None = None
    exam_config: dict[str, Any] | None = None


class LevelResponse(BaseSchema):
    id: uuid.UUID
    exam_id: uuid.UUID
    cefr_code: str
    total_pass_score: int
    display_order: int
    is_free: bool
    exam_config: dict[str, Any] | None
    subject_count: int = 0


class LevelWithSubjectsResponse(LevelResponse):
    """Level avec subjects + modules + teile (sans questions)."""
    subjects: list[SubjectWithModulesResponse] = []


# ─── Exam ────────────────────────────────────

class ExamCreateRequest(BaseSchema):
    provider: str = Field(max_length=50)
    name: str = Field(max_length=150)
    slug: str = Field(max_length=80, pattern=r"^[a-z0-9_]+$")
    description: str | None = None
    is_active: bool = True


class ExamUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, max_length=150)
    description: str | None = None
    is_active: bool | None = None


class ExamListResponse(BaseSchema):
    id: uuid.UUID
    provider: str
    name: str
    slug: str
    description: str | None
    is_active: bool
    levels: list[LevelResponse] = []


class ExamDetailResponse(ExamListResponse):
    """Vue détail — exam + levels + subjects + modules + teile."""
    levels: list[LevelWithSubjectsResponse] = []
    created_at: datetime


# ─── Catalogue enrichi (frontend) ────────────

class LevelAccessResponse(BaseSchema):
    id: uuid.UUID
    cefr_code: str
    total_pass_score: int
    display_order: int
    is_free: bool
    has_access: bool
    subject_count: int = 0
    price: int | None = None


class ExamCatalogResponse(BaseSchema):
    id: uuid.UUID
    provider: str
    name: str
    slug: str
    description: str | None
    levels: list[LevelAccessResponse] = []