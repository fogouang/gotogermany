"""
app/modules/training_sessions/models.py
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.centers.models import Branch
    from app.modules.exams.models import Level


class TrainingSession(Base, UUIDMixin, TimestampMixin):
    """
    Une cohorte niveau+date au sein d'une succursale (ex. "A1 du 15/08/2026").
    Créée par le staff du centre (directeur ou secrétaire) à la demande —
    plusieurs TrainingSession du même niveau peuvent coexister avec des
    dates de début différentes.
    """
    __tablename__ = "training_sessions"

    branch_id: Mapped[UUID] = mapped_column(
        ForeignKey("branches.id"), nullable=False, index=True
    )
    level_id: Mapped[UUID] = mapped_column(
        ForeignKey("levels.id"), nullable=False, index=True
    )
    label: Mapped[str | None] = mapped_column(String(150), nullable=True)

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    branch: Mapped["Branch"] = relationship("Branch", lazy="noload")
    level: Mapped["Level"] = relationship("Level", lazy="noload")
    teacher_links: Mapped[list["TrainingSessionTeacher"]] = relationship(
        "TrainingSessionTeacher", back_populates="training_session", lazy="noload"
    )
    student_links: Mapped[list["TrainingSessionStudent"]] = relationship(
        "TrainingSessionStudent", back_populates="training_session", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<TrainingSession branch={self.branch_id} level={self.level_id} start={self.start_date}>"


class TrainingSessionTeacher(Base, UUIDMixin, TimestampMixin):
    """Affectation enseignant↔session — many-to-many."""
    __tablename__ = "training_session_teachers"
    __table_args__ = (
        UniqueConstraint("training_session_id", "teacher_id", name="uq_session_teacher"),
    )

    training_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("training_sessions.id"), nullable=False, index=True
    )
    teacher_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    training_session: Mapped["TrainingSession"] = relationship(
        "TrainingSession", back_populates="teacher_links", lazy="noload"
    )
    teacher: Mapped["User"] = relationship("User", lazy="noload")

    def __repr__(self) -> str:
        return f"<TrainingSessionTeacher session={self.training_session_id} teacher={self.teacher_id}>"


class TrainingSessionStudent(Base, UUIDMixin, TimestampMixin):
    """Affectation étudiant↔session — porte l'historique (enrolled_at/ended_at)."""
    __tablename__ = "training_session_students"
    __table_args__ = (
        UniqueConstraint("training_session_id", "student_id", name="uq_session_student"),
    )

    training_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("training_sessions.id"), nullable=False, index=True
    )
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    training_session: Mapped["TrainingSession"] = relationship(
        "TrainingSession", back_populates="student_links", lazy="noload"
    )
    student: Mapped["User"] = relationship("User", lazy="noload")

    def __repr__(self) -> str:
        return f"<TrainingSessionStudent session={self.training_session_id} student={self.student_id}>"


class TeacherStudentComment(Base, UUIDMixin, TimestampMixin):
    """Commentaire libre d'un enseignant sur un étudiant (ex. signaler une
    faiblesse). Visible par l'auteur, le directeur du centre, et tout autre
    enseignant partageant une session active avec cet étudiant."""
    __tablename__ = "teacher_student_comments"

    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    comment: Mapped[str] = mapped_column(String(2000), nullable=False)

    teacher: Mapped["User"] = relationship("User", foreign_keys=[teacher_id], lazy="noload")
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id], lazy="noload")

    def __repr__(self) -> str:
        return f"<TeacherStudentComment teacher={self.teacher_id} student={self.student_id}>"