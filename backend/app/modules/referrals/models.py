"""
app/modules/referrals/models.py

Système de parrainage simple, réservé aux ambassadeurs (utilisateurs
désignés par l'admin). Indépendant de promo_codes, qui reste dédié
aux ventes tierces avec commission cash contractuelle.
"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


class ReferralEarning(Base, UUIDMixin, TimestampMixin):
    """Un gain pour l'ambassadeur, créé quand un de ses filleuls
    effectue un paiement (automatique ou validé manuellement). Une
    ligne par paiement récompensé — traçabilité complète pour le
    dashboard et un futur export comptable."""
    __tablename__ = "referral_earnings"

    __table_args__ = (
        UniqueConstraint("payment_id", name="uq_referral_earning_payment"),
    )

    referrer_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    referred_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Montant du gain en FCFA — calculé une fois au moment du paiement,
    # jamais recalculé après coup même si le taux global change plus tard.
    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<ReferralEarning referrer={self.referrer_user_id} amount={self.amount}>"