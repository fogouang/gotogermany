"""
app/modules/exam_sessions/models.py

Deux tables :
  - ExamSession        → une tentative complète d'un user sur un sujet précis
  - ExamSessionAnswer  → la réponse d'un user à une question donnée

Flow :
  1. User démarre → on choisit un subject (aléatoire ou séquentiel)
                  → ExamSession(status=IN_PROGRESS, subject_id=...)
  2. User répond  → ExamSessionAnswer upsert à chaque réponse
  3. User soumet  → score calculé pour les auto-correctable
                  → status → COMPLETED (ou PENDING_REVIEW si free_text/oral)

Accès :
  - ExamAccess pointe vers exam_id (l'étudiant achète TELC B1)
  - ExamSession pointe vers subject_id (le sujet précis joué)
  - On vérifie : ExamAccess.exam_id == Subject.level.exam_id
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, Boolean,
    DateTime, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


if TYPE_CHECKING:
    from app.modules.questions.models import Question
    from app.modules.users.models import User
    from app.modules.exams.models import Subject


class ExamSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exam_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Gardé pour les vérifications d'accès sans jointure
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Le sujet précis joué dans cette session
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # IN_PROGRESS | COMPLETED | PENDING_REVIEW | ABANDONED
    status: Mapped[str] = mapped_column(
        String(20), default="IN_PROGRESS", nullable=False, index=True
    )

    # Score total sur 100
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Score par module : {"lesen": 72, "horen": 85, "schreiben": null}
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # True=réussi, False=échoué, None=pas encore déterminé
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relations
    user: Mapped["User"] = relationship(
        "User", back_populates="exam_sessions", lazy="noload"
    )
    subject: Mapped["Subject"] = relationship(
        "Subject", lazy="noload"
    )
    answers: Mapped[list["ExamSessionAnswer"]] = relationship(
        "ExamSessionAnswer",
        back_populates="session",
        lazy="noload",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ExamSession user:{self.user_id} "
            f"subject:{self.subject_id} [{self.status}]>"
        )


class ExamSessionAnswer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exam_session_answers"

    __table_args__ = (
        UniqueConstraint(
            "session_id", "question_id",
            name="uq_answer_session_question"
        ),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Structure variable selon question_type :
    #   richtig_falsch / ja_nein : {"answer": "richtig"}
    #   qcm_abc                  : {"answer": "b"}
    #   matching / selektives    : {"answer": "d"}
    #   zuordnung_speaker        : {"answer": "c"}
    #   qcm_gap_fill             : {"answer": "a"}
    #   word_bank_gap_fill       : {"answer": "h"}
    #   free_text                : {"text": "Liebe Lisa, ..."}
    #   oral_*                   : {"audio_file": "sessions/uuid/q12.webm"}
    user_answer: Mapped[dict] = mapped_column(JSONB, nullable=False)

    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    score_obtained: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    corrected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relations
    session: Mapped["ExamSession"] = relationship(
        "ExamSession", back_populates="answers", lazy="noload"
    )
    question: Mapped["Question"] = relationship(
        "Question", back_populates="answers", lazy="noload"
    )

    def __repr__(self) -> str:
        return (
            f"<Answer session:{self.session_id} "
            f"q:{self.question_id} correct:{self.is_correct}>"
        )