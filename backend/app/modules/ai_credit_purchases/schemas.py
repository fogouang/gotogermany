"""
app/modules/ai_credit_purchases/schemas.py
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal


# ============================================================================
# PRICING
# ============================================================================

class CreditPricingResponse(BaseModel):
    price_per_credit: int
    price_per_credit_eur: float | None = None   # None : pas de paiement par carte
    min_purchase: int
    max_purchase: int
    examples: list[dict] = []
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PURCHASE — User (pawaPay)
# ============================================================================

class CreditPurchaseRequest(BaseModel):
    credits: int = Field(..., ge=5, le=500)
    phone_number: str = Field(..., description="Numéro Mobile Money")
    operator: str = Field(..., description="MTN ou ORANGE")

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        if v.upper() not in ("MTN", "ORANGE"):
            raise ValueError("operator doit être MTN ou ORANGE")
        return v.upper()


class CreditPurchaseResponse(BaseModel):
    payment_id: UUID
    invoice_number: str
    credits: int
    price_per_credit: float
    total_amount: float
    payment_status: str
    transaction_reference: str | None = None
    model_config = ConfigDict(from_attributes=True)

class CreditCardPurchaseRequest(BaseModel):
    """Achat de crédits par carte (Stripe, en euros)."""
    credits: int = Field(..., ge=5, le=500)
    # Langue de l'élève, pour le retour sur /fr/..., /en/..., /de/...
    locale: Literal["fr", "en", "de"] = "fr"


class CreditCardPurchaseResponse(BaseModel):
    payment_id: UUID
    transaction_reference: str
    checkout_url: str      # page Stripe vers laquelle rediriger l'élève
    credits: int
    amount_eur: float
    
# ============================================================================
# MANUAL GRANT — Admin
# ============================================================================

class ManualCreditGrantRequest(BaseModel):
    user_id: UUID
    credits: int = Field(..., ge=1, le=1000)


class ManualCreditGrantResponse(BaseModel):
    user_id: UUID
    credits_granted: int
    new_balance: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# HISTORY
# ============================================================================

class CreditPurchaseHistoryItem(BaseModel):
    id: UUID
    payment_id: UUID
    credits_purchased: int
    price_per_credit: float
    total_amount: float
    payment_method: str
    payment_status: str
    transaction_reference: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    charged_amount: float | None = None      # montant payé par carte (euros)
    charged_currency: str | None = None


class CreditPurchaseHistoryResponse(BaseModel):
    purchases: list[CreditPurchaseHistoryItem]
    total_spent: float
    total_credits_purchased: int


# ============================================================================
# BALANCE
# ============================================================================

class CreditBalanceResponse(BaseModel):
    ai_credits: int
    price_per_credit: int