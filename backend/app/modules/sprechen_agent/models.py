"""
sprechen_agent.models
========================
SQLAlchemy models — the only things in this module actually persisted
to Postgres. Live session state (session_state.py) never touches this
table; a row is written exactly once, when grading.py finishes and
service.py calls repository.py to save the result.

NOTE: adjust the Base import below to match your actual shared base.
get_db is confirmed to live at `app.shared.database.session` (per
users/router.py) — Base most likely sits alongside it in that same
module, or in a sibling `app.shared.database.base`. Adjust accordingly;
everything else here follows the same UUID-pk + JSONB pattern your
other modules already use.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database.base import Base, UUIDMixin, TimestampMixin

class SprechenSession(Base):
    """One completed (or abandoned) Sprechen agent session.

    Written once at the end of the session lifecycle — there is no
    partial/in-progress row. If a session is abandoned before grading,
    no row is created at all (nothing to show the student).
    """

    __tablename__ = "sprechen_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False
    )

    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # "goethe" | "telc" | "oesd"
    level: Mapped[str] = mapped_column(String(10), nullable=False)      # "B1" | "B2" | ...

    # Per-Teil breakdown, matches schemas.TeilGradingOut shape — kept
    # as JSONB rather than a child table since it's read-only after
    # creation and always consumed as a whole per session.
    teile_breakdown: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)

    total_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    total_max_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)

    strengths: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    improvement_areas: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    # Full transcript archive — one entry per turn, same shape as
    # session_state.TranscriptEntry. Kept for dispute resolution /
    # future re-grading, not surfaced in the default history view.
    transcript: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)

    # Which Live provider was used, mainly for cost/reliability
    # analysis later (e.g. "did the Gemini->OpenAI fallback fire?").
    live_provider_used: Mapped[str] = mapped_column(String(20), nullable=False, default="gemini")

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships — uncomment / adjust once User and Subject models
    # are importable here without a circular import.
    # student = relationship("User", back_populates="sprechen_sessions")
    # subject = relationship("Subject", back_populates="sprechen_sessions")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<SprechenSession id={self.id} student={self.student_id} "
            f"provider={self.provider} level={self.level} "
            f"score={self.total_score}/{self.total_max_score}>"
        )