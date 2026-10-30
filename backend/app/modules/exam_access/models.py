"""
app/modules/exam_access/models.py

Détermine si un user peut accéder à un niveau.

Deux sortes de niveaux :
  - level_id : niveau du catalogue des examens (B1, B2...)
  - sd_level : niveau Start Deutsch ("A1" ou "A2"), sans ligne dans le catalogue
Une ligne porte l'un ou l'autre, jamais les deux.

Création :
  - access_type="paid"  → après Payment(status=COMPLETED) (pawaPay, manuel, activation)
  - access_type="admin" → accordé par l'admin

Vérification : ligne active (expires_at NULL ou futur) sur le niveau.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime
from sqlalchemy import CheckConstraint, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


if TYPE_CHECKING:
    from app.modules.exams.models import Level
    from app.modules.payments.models import Payment
    from app.modules.users.models import User


class ExamAccess(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exam_access"

    __table_args__ = (
        UniqueConstraint("user_id", "level_id", name="uq_exam_access_user_level"),
        UniqueConstraint("user_id", "sd_level", name="uq_exam_access_user_sd_level"),
        CheckConstraint(
            "(level_id IS NOT NULL) <> (sd_level IS NOT NULL)",
            name="ck_exam_access_one_level",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Niveau du catalogue des examens (B1, B2...)
    level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("levels.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    # Niveau Start Deutsch : "A1" ou "A2"
    sd_level: Mapped[str | None] = mapped_column(String(5), nullable=True, index=True)

    # "paid" | "admin"
    access_type: Mapped[str] = mapped_column(String(10), nullable=False)

    # Lien vers le paiement qui a généré cet accès
    # NULL pour les accès accordés par l'admin
    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )

    # NULL = accès permanent
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="exam_accesses", lazy="noload")
    level: Mapped["Level | None"] = relationship("Level", back_populates="exam_accesses", lazy="noload")
    payment: Mapped["Payment | None"] = relationship(
        "Payment", lazy="noload", foreign_keys=[payment_id]
    )

    @property
    def is_active(self) -> bool:
        """Accès valide si pas d'expiration ou expiration future."""
        if self.expires_at is None:
            return True
        from datetime import timezone
        return self.expires_at > datetime.now(timezone.utc)

    def __repr__(self) -> str:
        level = self.sd_level or self.level_id
        return f"<ExamAccess user:{self.user_id} level:{level} ({self.access_type})>"