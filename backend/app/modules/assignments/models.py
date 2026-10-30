"""
app/modules/assignments/models.py

Devoirs donnés par un enseignant à partir de la banque de sujets privés.
Deux sortes de sujets :
- examen B1/B2 (subject_id), passé avec le moteur d'examen (ExamSession) ;
- Start Deutsch A1/A2 (sd_subject_id), passé avec le lecteur Start Deutsch.
"""
from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Float, ForeignKey, String, Text,
    UniqueConstraint, false,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


class Assignment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assignments"
    __table_args__ = (
        CheckConstraint(
            "(subject_id IS NOT NULL) <> (sd_subject_id IS NOT NULL)",
            name="ck_assignment_one_subject",
        ),
    )

    center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    sd_subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_subjects.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_cancelled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default=false()
    )

    @property
    def kind(self) -> str:
        return "start_deutsch" if self.sd_subject_id else "exam"


class AssignmentTarget(Base, UUIDMixin, TimestampMixin):
    """Une classe entière OU un élève précis."""
    __tablename__ = "assignment_targets"
    __table_args__ = (
        CheckConstraint(
            "(training_session_id IS NOT NULL) <> (student_id IS NOT NULL)",
            name="ck_assignment_target_one",
        ),
    )

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    training_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_sessions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    student_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )


class AssignmentSubmission(Base, UUIDMixin, TimestampMixin):
    """Copie d'un élève. Créée au premier démarrage du devoir."""
    __tablename__ = "assignment_submissions"
    __table_args__ = (
        UniqueConstraint("assignment_id", "student_id", name="uq_assignment_submission_student"),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'submitted', 'graded')",
            name="ck_assignment_submission_status",
        ),
    )

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exam_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exam_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Copie d'un devoir Start Deutsch
    sd_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, server_default="pending"
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    graded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Score final sur 100 (même échelle que ExamSession.score, Start Deutsch compris)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Commentaire général de l'enseignant (interne, non visible par l'élève)
    teacher_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Copie annotée déposée par l'enseignant (interne)
    annotated_file: Mapped[str | None] = mapped_column(String(255), nullable=True)