"""
app/modules/sales/schemas.py
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, model_validator

from app.shared.schemas.base import BaseSchema

PartnerType = Literal["center", "ambassador"]
RuleType = Literal["percent", "fixed"]


# ── Règles de commission ─────────────────────────────────

class CommissionRuleCreate(BaseSchema):
    partner_type: PartnerType
    center_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    plan_id: uuid.UUID | None = None
    rule_type: RuleType
    value: Decimal = Field(ge=0)

    @model_validator(mode="after")
    def check_consistency(self):
        if self.partner_type == "center" and self.user_id is not None:
            raise ValueError("Une règle de centre ne peut pas viser un ambassadeur.")
        if self.partner_type == "ambassador" and self.center_id is not None:
            raise ValueError("Une règle d'ambassadeur ne peut pas viser un centre.")
        if self.rule_type == "percent" and self.value > 100:
            raise ValueError("Un pourcentage ne peut pas dépasser 100.")
        return self


class CommissionRuleUpdate(BaseSchema):
    rule_type: RuleType | None = None
    value: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


class CommissionRuleResponse(BaseSchema):
    id: uuid.UUID
    partner_type: str
    center_id: uuid.UUID | None
    user_id: uuid.UUID | None
    plan_id: uuid.UUID | None
    rule_type: str
    value: float
    is_active: bool
    created_at: datetime


# ── Activation ───────────────────────────────────────────

class ActivationRequest(BaseSchema):
    student_id: uuid.UUID
    level_id: uuid.UUID
    plan_id: uuid.UUID


class PartnerSaleResponse(BaseSchema):
    id: uuid.UUID
    payment_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    plan_name: str | None
    level_id: uuid.UUID | None
    direction: str
    price: int
    partner_share: int
    platform_share: int
    amount_due: int
    settled_amount: int
    remaining: int
    rule_type: str
    rule_value: float
    due_at: datetime | None
    is_overdue: bool
    status: str
    created_at: datetime
    is_trial: bool = False      # activation offerte pendant l'essai du centre


class ActivationResponse(BaseSchema):
    sale: PartnerSaleResponse
    access_expires_at: datetime


# ── Partenaires ──────────────────────────────────────────

class PartnerSettingsUpdate(BaseSchema):
    can_activate: bool | None = None
    # Envoyer null explicitement pour retirer le plafond
    unpaid_limit: int | None = Field(default=None, ge=0)
    payment_delay_hours: int | None = Field(default=None, ge=1, le=720)
    # Période d'essai (centres uniquement) : null explicite sur trial_ends_at = fin de l'essai
    trial_ends_at: datetime | None = None
    trial_activations_left: int | None = Field(default=None, ge=0, le=500)


class PartnerSummaryResponse(BaseSchema):
    partner_type: str
    partner_id: uuid.UUID
    name: str
    can_activate: bool
    unpaid_limit: int | None
    payment_delay_hours: int
    owed_to_platform: int       # ce que le partenaire doit à GoToGermany
    owed_to_partner: int        # ce que GoToGermany doit au partenaire
    net_balance: int            # > 0 : le partenaire doit ; < 0 : GoToGermany doit
    overdue_amount: int
    overdue_count: int
    is_blocked: bool
    block_reason: str | None
    earned_total: int = 0       # part du partenaire sur toutes ses ventes
    trial_active: bool = False
    trial_ends_at: datetime | None = None
    trial_activations_left: int = 0


# ── Règlements ───────────────────────────────────────────

class SettlementCreate(BaseSchema):
    partner_type: PartnerType
    partner_id: uuid.UUID
    direction: Literal["to_platform", "to_partner"]
    amount: int = Field(gt=0)
    method: str = Field(min_length=2, max_length=30)   # mobile_money, especes, virement...
    reference: str | None = Field(default=None, max_length=255)
    note: str | None = Field(default=None, max_length=255)


class SettlementResponse(BaseSchema):
    id: uuid.UUID
    center_id: uuid.UUID | None
    user_id: uuid.UUID | None
    direction: str
    amount: int
    method: str
    reference: str | None
    note: str | None
    validated_by: uuid.UUID | None
    created_at: datetime


# ── Chiffre de la plateforme (admin) ─────────────────────

class PlatformRevenueResponse(BaseSchema):
    """Chiffre de la plateforme, en FCFA."""
    gross_total: int
    commissions_total: int
    net_total: int
    gross_month: int
    commissions_month: int
    net_month: int
    direct_total: int           # en ligne + paiements manuels
    partner_total: int          # ventes activées par les centres et ambassadeurs