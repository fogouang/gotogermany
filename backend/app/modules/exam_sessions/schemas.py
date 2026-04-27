"""
app/modules/exam_sessions/schemas.py
"""
import uuid
from datetime import datetime
from typing import Any
from app.shared.schemas.base import BaseSchema


class SessionStartRequest(BaseSchema):
    exam_id: uuid.UUID
    subject_id: uuid.UUID | None = None


class AnswerSubmitRequest(BaseSchema):
    question_id: uuid.UUID
    user_answer: dict[str, Any]


class BulkAnswerSubmitRequest(BaseSchema):
    answers: list[AnswerSubmitRequest]


class AnswerSubmitResponse(BaseSchema):
    question_id: uuid.UUID
    user_answer: dict[str, Any]
    is_correct: bool | None
    score_obtained: float | None
    correct_answer: dict[str, Any] | None


class AnswerDetailResponse(BaseSchema):
    question_id: uuid.UUID
    question_number: int
    question_type: str
    user_answer: dict[str, Any]
    correct_answer: dict[str, Any] | None
    is_correct: bool | None
    score_obtained: float | None
    points_possible: int
    feedback: dict[str, Any] | None
    corrected_at: datetime | None


class SessionStartResponse(BaseSchema):
    session_id: uuid.UUID
    exam_id: uuid.UUID
    exam_name: str
    subject_id: uuid.UUID
    subject_number: int
    subject_name: str | None
    status: str
    started_at: datetime
    modules: list[dict[str, Any]] = []
    existing_answers: dict[str, Any] = {}


class SessionListResponse(BaseSchema):
    id: uuid.UUID
    exam_id: uuid.UUID
    exam_name: str
    exam_slug: str
    subject_id: uuid.UUID
    subject_number: int
    status: str
    score: float | None
    passed: bool | None
    started_at: datetime
    submitted_at: datetime | None
    duration_seconds: int | None


class TeilResultResponse(BaseSchema):
    teil_number: int
    format_type: str
    max_score: int
    score_obtained: float
    answers: list[AnswerDetailResponse] = []


class ModuleResultResponse(BaseSchema):
    slug: str
    name: str
    max_score: int
    score_obtained: float | None
    is_corrected: bool
    teile: list[TeilResultResponse] = []


class SessionResultResponse(BaseSchema):
    session_id: uuid.UUID
    exam_id: uuid.UUID
    exam_name: str
    subject_id: uuid.UUID
    subject_number: int
    status: str
    score: float | None
    score_breakdown: dict[str, Any] | None
    passed: bool | None
    total_pass_score: int
    started_at: datetime
    submitted_at: datetime | None
    duration_seconds: int | None
    modules: list[ModuleResultResponse] = []
    result_message: str | None


class ActiveSessionResponse(BaseSchema):
    session_id: uuid.UUID
    exam_id: uuid.UUID
    exam_name: str
    subject_id: uuid.UUID
    subject_number: int
    status: str
    started_at: datetime
    answered_questions: int
    total_questions: int