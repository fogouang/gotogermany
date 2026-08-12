"""
app/modules/live_session/schemas.py
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .models import LiveSessionStatus


class CreateLiveSessionRequest(BaseModel):
    student_id: UUID
    subject_id: UUID


class LiveSessionResponse(BaseModel):
    id: UUID
    examiner_id: UUID
    student_id: UUID
    subject_id: UUID
    status: LiveSessionStatus
    created_at: datetime
    prep_started_at: datetime | None
    live_started_at: datetime | None
    ended_at: datetime | None
    examiner_notes: str | None
    notes_sent_at: datetime | None
    student_name: str | None
    examiner_name: str | None

    model_config = {"from_attributes": True}

class SubmitNotesRequest(BaseModel):
    notes: str = Field(min_length=1, max_length=5000)


class LiveSessionListResponse(BaseModel):
    items: list[LiveSessionResponse]
    total: int


class SubjectTeilContent(BaseModel):
    teil_number: int
    name: str | None = None
    instructions: str | None = None
    content_points: list[str] = Field(default_factory=list)
    themes: dict | None = None
    diskussion_titel: str | None = None
    diskussion_thema: str | None = None
    scenario: str | None = None
    tasks: list[str] = Field(default_factory=list)


class SubjectContentResponse(BaseModel):
    subject_id: UUID
    provider: str
    level: str
    teile: list[SubjectTeilContent]