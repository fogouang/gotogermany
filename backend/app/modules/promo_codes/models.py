"""
app/modules/promo_codes/models.py
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


if TYPE_CHECKING:
    from app.modules.partners.models import Partner
    from app.modules.payments.models import Payment


class PromoCode(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "promo_codes"

    __table_args__ = (
        # discount_value doit être positif
        CheckConstraint("discount_value > 0", name="ck_promo_discount_positive"),
        # si percent, discount_value <= 100
        CheckConstraint(
            "discount_type != 'percent' OR discount_value <= 100",
            name="ck_promo_percent_max_100",
        ),
        # commission_rate entre 0 et 100
        CheckConstraint(
            "commission_rate >= 0 AND commission_rate <= 100",
            name="ck_promo_commission_range",
        ),
    )

    # Lien optionnel vers un partenaire
    # NULL = promo interne (ex: promo saisonnière sans commission)
    partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # 'percent' | 'fixed'
    discount_type: Mapped[str] = mapped_column(String(10), nullable=False)

    # Si percent → ex: 20 (= 20%)  |  Si fixed → ex: 1000 (= 1000 FCFA)
    discount_value: Mapped[int] = mapped_column(Integer, nullable=False)

    # % de commission reversé au partenaire sur chaque paiement
    # 0 si pas de partenaire ou promo sans commission
    commission_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # NULL = usages illimités
    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # NULL = pas d'expiration
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relations
    partner: Mapped["Partner | None"] = relationship(
        "Partner", back_populates="promo_codes", lazy="noload"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="promo_code", lazy="noload"
    )

    @property
    def is_exhausted(self) -> bool:
        """True si le code a atteint sa limite d'utilisations."""
        return self.max_uses is not None and self.used_count >= self.max_uses

    def compute_discount(self, amount: int) -> int:
        """Retourne le montant de la réduction en entier (FCFA)."""
        if self.discount_type == "percent":
            return int(amount * self.discount_value / 100)
        return min(self.discount_value, amount)  # fixed, plafonné au montant

    def __repr__(self) -> str:
        return f"<PromoCode {self.code} ({self.discount_type}:{self.discount_value})>"