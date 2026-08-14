"""
app/modules/live_session/models.py

Session Sprechen en direct avec un examinateur réel du centre (branch_secretary
ou center_director), en remplacement du partenaire IA — pour les centres qui
veulent évaluer eux-mêmes, comme à l'examen officiel.

Ne remplace PAS le module sprechen_agent existant (mode solo avec IA) : les
deux coexistent, ce module est entièrement séparé.

Hiérarchie : LiveSession → (examiner: User, student: User, subject: Subject)
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.exams.models import Subject


class LiveSessionStatus(str, enum.Enum):
    waiting = "waiting"      # créée par l'examinateur, candidat pas encore rejoint
    preparing = "preparing"  # les deux sont connectés, prépa 20min/3 Teile en cours
    live = "live"            # pont audio actif, épreuve en cours
    ended = "ended"          # terminée normalement
    cancelled = "cancelled"  # annulée avant ou pendant


class LiveSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "live_sessions"

    examiner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Staff du centre (branch_secretary, center_director) ou enseignant "
            "assigné via une training_session — qui lance et mène la session",
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Sujet Sprechen existant, choisi par l'examinateur dans la banque déjà en place",
    )

    status: Mapped[LiveSessionStatus] = mapped_column(
        Enum(LiveSessionStatus, name="live_session_status"),
        default=LiveSessionStatus.waiting,
        nullable=False,
        server_default=LiveSessionStatus.waiting.value,
    )

    prep_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    live_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Notes libres de l'examinateur (pas de grille/barème structuré — le centre
    # gère sa propre grille en dehors du système). Rédigées pendant ou juste
    # après la session, envoyées/affichées au student une fois la session
    # marquée "ended". notes_sent_at reste NULL tant que l'étudiant n'a pas
    # encore reçu/vu ses notes.
    examiner_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relations
    examiner: Mapped["User"] = relationship(
        "User", foreign_keys=[examiner_id], lazy="noload"
    )
    student: Mapped["User"] = relationship(
        "User", foreign_keys=[student_id], lazy="noload"
    )
    subject: Mapped["Subject"] = relationship(
        "Subject", foreign_keys=[subject_id], lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<LiveSession {self.id} status={self.status} examiner={self.examiner_id} student={self.student_id}>"