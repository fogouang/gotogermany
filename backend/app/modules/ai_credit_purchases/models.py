"""
app/modules/ai_credit_purchases/models.py

Achat de crédits IA pour la correction Schreiben.
Système simplifié : prix fixe par crédit, pas de plans.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database.base import BaseModel

if TYPE_CHECKING:
    from app.modules.payments.models import Payment
    from app.modules.users.models import User


class AICreditPurchase(BaseModel):
    """
    Achat de crédits IA pour le simulateur Schreiben.

    Flow:
    1. User initie un achat via POST /ai-credits/purchase
    2. My-CoolPay traite le paiement
    3. Webhook → crédits ajoutés à User.ai_credits
    4. AICreditPurchase enregistré pour l'historique/facture

    Prix fixe défini dans settings (PRICE_PER_AI_CREDIT).
    Pas de plans — l'utilisateur choisit la quantité.
    """

    __tablename__ = "ai_credit_purchases"

    # ── Liens ────────────────────────────────────────────────
    payment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        doc="Référence vers le paiement My-CoolPay (1-to-1)",
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Dénormalisé pour requêtes rapides sans jointure Payment",
    )

    # ── Détails achat ─────────────────────────────────────────
    credits_purchased: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Quantité de crédits achetés",
    )

    price_per_credit: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        doc="Prix unitaire au moment de l'achat (snapshot historique)",
    )

    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        doc="Montant total = credits_purchased × price_per_credit",
    )

    # ── Note admin (paiement manuel) ──────────────────────────
    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Note admin pour paiement manuel (ex: 'Virement reçu le 12/06')",
    )

    # ── Relationships ─────────────────────────────────────────
    payment: Mapped["Payment"] = relationship("Payment")
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"AICreditPurchase(id={self.id}, "
            f"user_id={self.user_id}, "
            f"credits={self.credits_purchased}, "
            f"amount={self.total_amount} FCFA)"
        )