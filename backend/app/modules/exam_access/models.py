"""
app/modules/exam_access/models.py

Détermine si un user peut accéder à un exam.

Deux cas de création :
  - access_type="free"  → créé automatiquement à l'inscription
                          pour tous les Level(is_free=True)
  - access_type="paid"  → créé par le webhook handler après
                          Payment(status=COMPLETED)

Vérification d'accès (dans les dependencies FastAPI) :
  SELECT * FROM exam_access
  WHERE user_id = :uid AND exam_id = :eid
  AND (expires_at IS NULL OR expires_at > NOW())
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.exams.models import Exam
    from app.modules.payments.models import Payment
    from app.modules.users.models import User


class ExamAccess(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exam_access"

    __table_args__ = (
        # Un user ne peut avoir qu'un accès par exam
        UniqueConstraint("user_id", "exam_id", name="uq_exam_access_user_exam"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # "free" | "paid"
    access_type: Mapped[str] = mapped_column(String(10), nullable=False)

    # Lien vers le paiement qui a généré cet accès
    # NULL pour les accès gratuits
    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )

    # NULL = accès permanent (cas standard pour les achats one-time)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="exam_accesses", lazy="noload")
    exam: Mapped["Exam"] = relationship("Exam", back_populates="exam_accesses", lazy="noload")
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
        return f"<ExamAccess user:{self.user_id} exam:{self.exam_id} ({self.access_type})>"