"""
app/modules/enrollments/models.py
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
import enum
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.centers.models import Branch


class CursusLevel(str, enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"


class CursusStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class LevelEnrollmentStatus(str, enum.Enum):
    pending_inscription = "pending_inscription"  # frais d'inscription pas encore payés
    active = "active"                              # inscription validée, formation en cours
    completed = "completed"
    abandoned = "abandoned"


class FormationPaymentType(str, enum.Enum):
    inscription = "inscription"
    formation = "formation"


class Cursus(Base, UUIDMixin, TimestampMixin):
    """
    Parcours global d'un élève au sein d'un centre : niveau de départ -> niveau visé.
    Totalement indépendant du système d'accès aux examens (Level/ExamAccess/target_level_id).
    """
    __tablename__ = "cursus"

    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    branch_id: Mapped[UUID] = mapped_column(ForeignKey("branches.id"), nullable=False, index=True)

    start_level: Mapped[CursusLevel] = mapped_column(Enum(CursusLevel, name="cursus_level"), nullable=False)
    target_level: Mapped[CursusLevel] = mapped_column(Enum(CursusLevel, name="cursus_level"), nullable=False)

    status: Mapped[CursusStatus] = mapped_column(
        Enum(CursusStatus, name="cursus_status"),
        default=CursusStatus.in_progress,
        nullable=False,
        server_default=CursusStatus.in_progress.value,
    )

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id], lazy="noload")
    branch: Mapped["Branch"] = relationship("Branch", lazy="noload")
    level_enrollments: Mapped[list["LevelEnrollment"]] = relationship(
        "LevelEnrollment", back_populates="cursus", lazy="noload", order_by="LevelEnrollment.created_at"
    )

    def __repr__(self) -> str:
        return f"<Cursus student={self.student_id} {self.start_level}->{self.target_level}>"


class LevelEnrollment(Base, UUIDMixin, TimestampMixin):
    """
    Inscription d'un élève à un niveau précis de son cursus.
    Deux volets financiers distincts : frais d'inscription (bloquant) et frais
    de formation (payables librement — en une fois, à moitié, ou par tranches —
    une fois l'inscription validée).
    """
    __tablename__ = "level_enrollments"

    cursus_id: Mapped[UUID] = mapped_column(ForeignKey("cursus.id"), nullable=False, index=True)
    level: Mapped[CursusLevel] = mapped_column(Enum(CursusLevel, name="cursus_level"), nullable=False)

    inscription_fee_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    formation_fee_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[LevelEnrollmentStatus] = mapped_column(
        Enum(LevelEnrollmentStatus, name="level_enrollment_status"),
        default=LevelEnrollmentStatus.pending_inscription,
        nullable=False,
        server_default=LevelEnrollmentStatus.pending_inscription.value,
    )

    cursus: Mapped["Cursus"] = relationship("Cursus", back_populates="level_enrollments", lazy="noload")
    payments: Mapped[list["FormationPayment"]] = relationship(
        "FormationPayment", back_populates="enrollment", lazy="noload"
    )
    
    invoice_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<LevelEnrollment {self.level} status={self.status}>"


class FormationPayment(Base, UUIDMixin, TimestampMixin):
    """
    Paiement saisi manuellement par le staff du centre (secrétaire/directeur).
    Rattaché soit aux frais d'inscription, soit aux frais de formation d'un niveau.
    Le "reste à payer" se calcule dynamiquement (montant dû - somme des paiements),
    pas de plan de tranches figé en base.
    """
    __tablename__ = "formation_payments"

    enrollment_id: Mapped[UUID] = mapped_column(ForeignKey("level_enrollments.id"), nullable=False, index=True)
    payment_type: Mapped[FormationPaymentType] = mapped_column(
        Enum(FormationPaymentType, name="formation_payment_type"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)

    enrollment: Mapped["LevelEnrollment"] = relationship(
        "LevelEnrollment", back_populates="payments", lazy="noload"
    )
    recorder: Mapped["User"] = relationship("User", foreign_keys=[recorded_by], lazy="noload")

    def __repr__(self) -> str:
        return f"<FormationPayment id={self.id}>"