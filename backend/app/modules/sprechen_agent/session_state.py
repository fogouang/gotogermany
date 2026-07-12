"""
sprechen_agent.session_state
==============================
In-memory session state for a live Sprechen conversation.

NOT SQLAlchemy — nothing here is persisted as-is. models.py holds
the real DB table (the final graded result). This file only lives
for the duration of an active WebSocket session, kept in the
in-memory session store (a process-local dict for V1, see service.py).
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AgentRole(StrEnum):
    """What the AI is doing during a given sub-step of a Teil.

    Maps 1:1 to the format_type -> behavior table. A single Teil can
    walk through several of these in sequence (e.g. SILENT_LISTENER ->
    EXAMINER -> PRESENTER -> ... for a two-candidate Teil).
    """
    PARTNER = "partner"                    # free dialogue partner
    EXAMINER = "examiner"                  # comments + asks a question
    SILENT_LISTENER = "silent_listener"    # listens, minimal backchannel only
    PRESENTER = "presenter"                # AI itself delivers a monologue (Kandidat B)
    ASSIGNED_POSITION = "assigned_position"  # argues a fixed, possibly non-authentic stance


class SessionStatus(StrEnum):
    PENDING = "pending"           # created, Live connection not yet opened
    ACTIVE = "active"              # a Live segment is currently streaming
    BETWEEN_SEGMENTS = "between_segments"  # Live connection closed, transcript being carried over
    AWAITING_GRADING = "awaiting_grading"  # session ended, Claude call not yet run
    GRADED = "graded"
    ABANDONED = "abandoned"        # student disconnected / timed out, cleaned up


class ScoringSystem(StrEnum):
    """The 3 grading styles observed across providers — kept distinct
    so grading.py knows how to read scoring_criteria_raw without
    forcing a lossy conversion at ingestion time."""
    LETTER_TIER = "letter_tier"       # Goethe-style: sub-criteria with fixed point buckets
    POINT_TIER = "point_tier"          # telc-style: A/B/C/D tiers with fixed point values
    CONTINUOUS = "continuous"          # ÖSD-style: free 0..max score per criterion


# ---------------------------------------------------------------------------
# Sequence definition (derived from format_type + raw subject JSON)
# ---------------------------------------------------------------------------

class SequenceStep(BaseModel):
    """One sub-step within a Teil's spoken sequence.

    For a simple Teil (single format_type, no ablauf_schema, no
    kandidat_a/kandidat_b split) this list has exactly one entry.
    For a two-candidate Teil it typically has 6 (see the default
    alternating sequence).
    """
    order: int
    role: AgentRole
    agent_opens: bool = False
    # Free-form content this step needs injected into the prompt —
    # e.g. kandidat_b's theme/leitpunkte when role == PRESENTER.
    content: dict[str, Any] = Field(default_factory=dict)
    # Soft target only — never hard-enforced mid-speech.
    target_duration_seconds: int | None = None
    completed: bool = False


class TeilConfig(BaseModel):
    """Normalized view of a single Teil, built once when a session
    starts by reading the raw subject JSON already stored in DB.

    This is the output of the extraction layer discussed earlier —
    it does NOT duplicate the DB row, it's a derived, ephemeral view
    kept only for the lifetime of the session.
    """
    teil_number: int
    name: str
    format_type: str
    instructions: str
    duration_minutes: int
    preparation_minutes: int = 0
    # Normalized from leitpunkte / prompts / tasks / leitfragen / hinweis
    content_points: list[str] = Field(default_factory=list)
    sprachliche_mittel: list[str] = Field(default_factory=list)
    scoring_system: ScoringSystem
    scoring_criteria_raw: dict[str, Any] = Field(default_factory=dict)
    sequence: list[SequenceStep]


# ---------------------------------------------------------------------------
# Transcript
# ---------------------------------------------------------------------------

class TranscriptEntry(BaseModel):
    teil_number: int
    step_order: int
    speaker: str  # "student" | "agent"
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Session state — the thing that lives in the in-memory store
# ---------------------------------------------------------------------------

class SessionState(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    student_id: UUID
    subject_id: UUID          # FK to the exam subject row already in DB
    provider: str              # "goethe" | "telc" | "oesd"
    level: str                 # "B1" | "B2" | ...
    cefr_target: str           # usually == level, kept separate for A1/A2 J-variants etc.
    pass_threshold_percent: float = 60.0

    status: SessionStatus = SessionStatus.PENDING

    teile: list[TeilConfig]
    current_teil_index: int = 0
    current_step_index: int = 0

    transcript: list[TranscriptEntry] = Field(default_factory=list)

    # Live connection bookkeeping — set by live_client.py, read by
    # orchestrator.py to decide when to close/reopen a segment.
    live_connection_id: str | None = None
    live_provider: str = "gemini"   # "gemini" | "openai" — set on fallback

    started_at: datetime | None = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None

    def current_teil(self) -> TeilConfig:
        return self.teile[self.current_teil_index]

    def current_step(self) -> SequenceStep:
        return self.current_teil().sequence[self.current_step_index]

    def is_last_step_of_teil(self) -> bool:
        return self.current_step_index == len(self.current_teil().sequence) - 1

    def is_last_teil(self) -> bool:
        return self.current_teil_index == len(self.teile) - 1


# ---------------------------------------------------------------------------
# Grading contract (consumed by grading.py, produced for the frontend)
# ---------------------------------------------------------------------------

class CriterionScore(BaseModel):
    criterion_name: str
    score: float
    max_score: float
    comment: str | None = None


class TeilGrading(BaseModel):
    teil_number: int
    criteria: list[CriterionScore]
    teil_score: float
    teil_max_score: float


class GradingResult(BaseModel):
    session_id: UUID
    provider: str
    level: str
    teile: list[TeilGrading]
    total_score: float
    total_max_score: float
    pass_threshold_percent: float
    passed: bool
    strengths: list[str] = Field(default_factory=list)
    improvement_areas: list[str] = Field(default_factory=list)
    graded_at: datetime = Field(default_factory=datetime.utcnow)