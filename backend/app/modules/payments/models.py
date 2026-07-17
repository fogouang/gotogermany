"""
app/modules/payments/models.py

Flow My-CoolPay :
  1. User initie l'achat → on crée Payment(status=PENDING)
  2. On appelle My-CoolPay payin → on stocke mycoolpay_ref
  3. Webhook reçu → on update status COMPLETED ou FAILED
  4. Si COMPLETED → service crée ExamAccess automatiquement
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, DateTime, ForeignKey,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.shared.database.base import Base, UUIDMixin, TimestampMixin



if TYPE_CHECKING:
    from app.modules.exams.models import Level
    from app.modules.promo_codes.models import PromoCode
    from app.modules.users.models import User
    from app.modules.plans.models import Plan  


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"

    __table_args__ = (
        # mycoolpay_ref est unique quand il est renseigné
        UniqueConstraint("pawapay_deposit_id", name="uq_payment_pawapay_deposit_id"),
        # amount_paid ne peut pas dépasser amount_gross
        CheckConstraint("amount_paid <= amount_gross", name="ck_payment_amount_paid_lte_gross"),
        # amount_paid >= 0
        CheckConstraint("amount_paid >= 0", name="ck_payment_amount_paid_positive"),
        # commission_due >= 0
        CheckConstraint("commission_due >= 0", name="ck_payment_commission_positive"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    
    level_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("levels.id", ondelete="RESTRICT"), 
        nullable=True,
        index=True,
    )

    promo_code_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("promo_codes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    # Montant original avant réduction (en FCFA, entier)
    amount_gross: Mapped[int] = mapped_column(Integer, nullable=False)

    # Montant réellement payé après réduction
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False)

    # Commission calculée au moment du paiement et figée
    # = amount_paid * promo_code.commission_rate / 100
    # 0 si pas de code promo partenaire
    commission_due: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    currency: Mapped[str] = mapped_column(String(10), default="XAF", nullable=False)

    # PENDING | COMPLETED | FAILED | REFUNDED
    payment_status: Mapped[str] = mapped_column(
        String(20), default="PENDING", nullable=False, index=True
    )
    plan: Mapped["Plan"] = relationship("Plan", back_populates="payments", lazy="noload")
    # Référence interne générée avant l'appel My-CoolPay
    # Envoyée comme app_transaction_ref à My-CoolPay
    transaction_reference: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    invoice_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    pawapay_deposit_id: Mapped[str | None] = mapped_column(String(36), nullable=True)  # UUID pawaPay
    
    # Opérateur utilisé : "MTN", "ORANGE", etc.
    operator: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Données brutes du webhook My-CoolPay pour audit
    webhook_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Date de complétion effective
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Renseigné uniquement si ce paiement a été confirmé manuellement
    # (admin ou ambassadeur) plutôt qu'automatiquement via le webhook
    # pawaPay — traçabilité et audit.
    validated_manually_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    # Relations
    user: Mapped["User"] = relationship(
        "User", back_populates="payments", foreign_keys=[user_id], lazy="noload"
    )
    level: Mapped["Level"] = relationship("Level", back_populates="payments", lazy="noload")
    promo_code: Mapped["PromoCode | None"] = relationship(
        "PromoCode", back_populates="payments", lazy="noload"
    )

    @property
    def is_completed(self) -> bool:
        return self.payment_status == "COMPLETED"

    @property
    def discount_amount(self) -> int:
        return self.amount_gross - self.amount_paid

    def __repr__(self) -> str:
        return f"<Payment {self.transaction_reference} — {self.payment_status}>"