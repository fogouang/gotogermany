"""
app/modules/sales/models.py

Ventes réalisées via les partenaires (centres et ambassadeurs) et leurs règlements.

Sens d'une vente :
  - partner_owes  : le partenaire a encaissé l'élève (espèces, etc.) et activé
                    son compte. Il doit platform_share à GoToGermany avant due_at.
  - platform_owes : le filleul d'un ambassadeur a payé en ligne. GoToGermany
                    doit partner_share à l'ambassadeur.

amount_due est le montant attendu dans le sens de la vente ; settled_amount
progresse à chaque règlement (imputation des plus anciennes en premier).
"""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric,
    String, UniqueConstraint, true,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


class CommissionRule(Base, UUIDMixin, TimestampMixin):
    """
    Règle de commission. La plus précise l'emporte :
      partenaire + formule > partenaire > défaut + formule > défaut.
    Une règle "défaut" n'a ni center_id ni user_id.
    """
    __tablename__ = "commission_rules"
    __table_args__ = (
        CheckConstraint("partner_type IN ('center', 'ambassador')", name="ck_commission_partner_type"),
        CheckConstraint("rule_type IN ('percent', 'fixed')", name="ck_commission_rule_type"),
        CheckConstraint("value >= 0", name="ck_commission_value_positive"),
        CheckConstraint(
            "NOT (center_id IS NOT NULL AND user_id IS NOT NULL)",
            name="ck_commission_single_partner",
        ),
    )

    partner_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    center_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centers.id", ondelete="CASCADE"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=True, index=True
    )
    # percent : value = pourcentage (ex. 33.33) ; fixed : value = montant FCFA
    rule_type: Mapped[str] = mapped_column(String(10), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, server_default=true()
    )

    def __repr__(self) -> str:
        return f"<CommissionRule {self.partner_type} {self.rule_type}={self.value}>"


class PartnerSale(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "partner_sales"
    __table_args__ = (
        UniqueConstraint("payment_id", name="uq_partner_sale_payment"),
        CheckConstraint(
            "direction IN ('partner_owes', 'platform_owes')", name="ck_partner_sale_direction"
        ),
        CheckConstraint(
            "status IN ('due', 'partial', 'settled')", name="ck_partner_sale_status"
        ),
        CheckConstraint(
            "(center_id IS NOT NULL) <> (user_id IS NOT NULL)", name="ck_partner_sale_one_partner"
        ),
        CheckConstraint(
            "settled_amount >= 0 AND settled_amount <= amount_due",
            name="ck_partner_sale_settled_range",
        ),
    )

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id", ondelete="SET NULL"), nullable=True
    )
    level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("levels.id", ondelete="SET NULL"), nullable=True
    )

    # Un seul des deux est renseigné
    center_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centers.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    # Secrétaire, directeur ou ambassadeur ayant activé (NULL pour une vente en ligne)
    activated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    direction: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    partner_share: Mapped[int] = mapped_column(Integer, nullable=False)
    platform_share: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_due: Mapped[int] = mapped_column(Integer, nullable=False)
    settled_amount: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, server_default="0"
    )

    # Règle figée au moment de la vente
    rule_type: Mapped[str] = mapped_column(String(10), nullable=False)
    rule_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Échéance (partner_owes uniquement)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(10), default="due", nullable=False, server_default="due", index=True
    )
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Activation offerte pendant la période d'essai du centre
    is_trial: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    
    def __repr__(self) -> str:
        return f"<PartnerSale {self.direction} due={self.amount_due} settled={self.settled_amount}>"


class PartnerSettlement(Base, UUIDMixin, TimestampMixin):
    """Règlement validé par l'admin, dans un sens ou dans l'autre."""
    __tablename__ = "partner_settlements"
    __table_args__ = (
        CheckConstraint(
            "direction IN ('to_platform', 'to_partner')", name="ck_partner_settlement_direction"
        ),
        CheckConstraint(
            "(center_id IS NOT NULL) <> (user_id IS NOT NULL)", name="ck_partner_settlement_one_partner"
        ),
        CheckConstraint("amount > 0", name="ck_partner_settlement_amount_positive"),
    )

    center_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centers.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    method: Mapped[str] = mapped_column(String(30), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    validated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class PartnerSettlementAllocation(Base, UUIDMixin, TimestampMixin):
    """Quelle part d'un règlement a soldé quelle vente (audit)."""
    __tablename__ = "partner_settlement_allocations"

    settlement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partner_settlements.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    sale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partner_sales.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)