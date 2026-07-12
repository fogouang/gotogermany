"""
sprechen_agent.schemas
========================
API-facing Pydantic contracts — what the frontend sends and receives
over the Sprechen WebSocket, plus the REST-facing grading response.

Deliberately thinner than session_state.SessionState: the frontend
never needs live_connection_id, raw scoring_criteria, or internal
sequence bookkeeping. This is the public surface only.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Inbound — frontend -> backend
# ---------------------------------------------------------------------------

class StartSessionRequest(BaseModel):
    """Sent once, over REST or as the first WebSocket message, to
    initialize a session for a subject the student picked from the
    filtered list (provider + level)."""
    student_id: UUID
    subject_id: UUID


class AudioChunkMessage(BaseModel):
    """Streamed repeatedly while the student is speaking. The raw
    bytes travel as a separate binary WebSocket frame — this message
    only carries the sequencing metadata."""
    type: Literal["audio_chunk"] = "audio_chunk"
    session_id: UUID
    sequence_number: int


class EndTurnMessage(BaseModel):
    """Sent by the frontend when the student explicitly signals they
    are done speaking (e.g. releases a push-to-talk button). Optional
    for formats using pure voice-activity detection, but recommended
    for predictable turn-taking."""
    type: Literal["end_turn"] = "end_turn"
    session_id: UUID


class AbandonSessionMessage(BaseModel):
    """Sent on graceful exit (student closes the tab intentionally).
    Distinguishes a clean abandon from a dropped connection detected
    server-side by heartbeat timeout — both end in ABANDONED, but this
    one skips the grace-period reconnection window."""
    type: Literal["abandon_session"] = "abandon_session"
    session_id: UUID


InboundMessage = Annotated[
    Union[AudioChunkMessage, EndTurnMessage, AbandonSessionMessage],
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# Outbound — backend -> frontend (pushed as the session progresses)
# ---------------------------------------------------------------------------

class SessionReadyEvent(BaseModel):
    type: Literal["session_ready"] = "session_ready"
    session_id: UUID
    total_teile: int
    first_teil_name: str


class TeilStartedEvent(BaseModel):
    """Pushed whenever the orchestrator moves to a new Teil. Frontend
    uses this to update the "Teil X / Y" header and swap in the
    relevant instructions/leitpunkte panel — same fields it already
    displays statically today."""
    type: Literal["teil_started"] = "teil_started"
    session_id: UUID
    teil_number: int
    teil_name: str
    instructions: str
    content_points: list[str]
    duration_minutes: int


class AgentSpeakingEvent(BaseModel):
    """Signals the frontend to show a visual "agent is speaking"
    state (e.g. waveform / avatar animation) rather than expecting
    student audio input."""
    type: Literal["agent_speaking"] = "agent_speaking"
    session_id: UUID


class StudentTurnEvent(BaseModel):
    """Signals the frontend it's the student's turn — mic can open."""
    type: Literal["student_turn"] = "student_turn"
    session_id: UUID


class TranscriptUpdateEvent(BaseModel):
    """Incremental transcript line, pushed as soon as it's available
    from the Live provider — lets the frontend optionally show a
    live caption, and lets the client confirm audio is being heard."""
    type: Literal["transcript_update"] = "transcript_update"
    session_id: UUID
    speaker: Literal["student", "agent"]
    text: str


class SessionEndedEvent(BaseModel):
    type: Literal["session_ended"] = "session_ended"
    session_id: UUID
    reason: Literal["completed", "abandoned", "error"]


OutboundEvent = Annotated[
    Union[
        SessionReadyEvent,
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
    comment: str | None = None


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


class SessionHistoryItem(BaseModel):
    """One row in the student's past-sessions list."""
    session_id: UUID
    provider: str
    level: str
    subject_name: str
    total_score: float
    total_max_score: float
    passed: bool
    completed_at: datetime


class SessionHistoryListResponse(BaseModel):
    """response_model for GET /history — matches the typed
    response_model= convention used throughout the codebase rather
    than returning a raw dict."""
    items: list[SessionHistoryItem]
    total: int