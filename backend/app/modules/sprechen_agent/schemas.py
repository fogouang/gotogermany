"""
sprechen_agent.schemas
========================
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal, TypeAlias, Union
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Inbound — frontend -> backend
# ---------------------------------------------------------------------------

class StartSessionRequest(BaseModel):
    student_id: UUID
    subject_id: UUID


class AudioChunkMessage(BaseModel):
    type: Literal["audio_chunk"] = "audio_chunk"
    session_id: UUID
    sequence_number: int


class EndTurnMessage(BaseModel):
    type: Literal["end_turn"] = "end_turn"
    session_id: UUID


class AbandonSessionMessage(BaseModel):
    type: Literal["abandon_session"] = "abandon_session"
    session_id: UUID


class ReadyToStartMessage(BaseModel):
    """Sent by the frontend once the student is done reviewing the
    preparation panel (or the local prep timer runs out) — signals
    the backend to open the actual Live segment."""
    type: Literal["ready_to_start"] = "ready_to_start"
    session_id: UUID


InboundMessage: TypeAlias = Annotated[
    Union[AudioChunkMessage, EndTurnMessage, AbandonSessionMessage, ReadyToStartMessage],
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# Outbound — backend -> frontend
# ---------------------------------------------------------------------------

class SessionReadyEvent(BaseModel):
    type: Literal["session_ready"] = "session_ready"
    session_id: UUID
    total_teile: int
    first_teil_name: str


class PreparationStartedEvent(BaseModel):
    """Pushed instead of immediately opening a Live segment, whenever
    the upcoming Teil has preparation_minutes > 0. Frontend shows a
    notes-taking panel with a countdown; sends ReadyToStartMessage
    when done (either by timer or an explicit button)."""
    type: Literal["preparation_started"] = "preparation_started"
    session_id: UUID
    teil_number: int
    teil_name: str
    instructions: str
    content_points: list[str]
    themes: dict[str, Any] | None = None
    preparation_minutes: int


class TeilStartedEvent(BaseModel):
    """Pushed whenever the orchestrator moves to a new Teil."""
    type: Literal["teil_started"] = "teil_started"
    session_id: UUID
    teil_number: int
    teil_name: str
    instructions: str
    content_points: list[str]
    themes: dict[str, Any] | None = None
    duration_minutes: int
    preparation_minutes: int = 0


class AgentSpeakingEvent(BaseModel):
    type: Literal["agent_speaking"] = "agent_speaking"
    session_id: UUID


class StudentTurnEvent(BaseModel):
    type: Literal["student_turn"] = "student_turn"
    session_id: UUID


class TranscriptUpdateEvent(BaseModel):
    type: Literal["transcript_update"] = "transcript_update"
    session_id: UUID
    speaker: Literal["student", "agent"]
    text: str


class SessionEndedEvent(BaseModel):
    type: Literal["session_ended"] = "session_ended"
    session_id: UUID
    reason: Literal["completed", "abandoned", "error"]


OutboundEvent: TypeAlias = Annotated[
    Union[
        SessionReadyEvent,
        PreparationStartedEvent,
        TeilStartedEvent,
        AgentSpeakingEvent,
        StudentTurnEvent,
        TranscriptUpdateEvent,
        SessionEndedEvent,
    ],
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# Grading — REST response once a session is scored
# ---------------------------------------------------------------------------

class CriterionScoreOut(BaseModel):
    criterion_name: str
    score: float
    max_score: float
    issue: str | None = None
    model_phrase: str | None = None
    tip: str | None = None


class TeilGradingOut(BaseModel):
    teil_number: int
    teil_name: str
    criteria: list[CriterionScoreOut]
    teil_score: float
    teil_max_score: float


class GradingResponse(BaseModel):
    session_id: UUID
    provider: str
    level: str
    teile: list[TeilGradingOut]
    total_score: float
    total_max_score: float
    passed: bool
    strengths: list[str]
    improvement_areas: list[str]
    graded_at: datetime
    previous_score_percent: float | None = None
    score_delta_percent: float | None = None


class SessionHistoryItem(BaseModel):
    session_id: UUID
    provider: str
    level: str
    subject_name: str
    total_score: float
    total_max_score: float
    passed: bool
    completed_at: datetime


class SessionHistoryListResponse(BaseModel):
    items: list[SessionHistoryItem]
    total: int