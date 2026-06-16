"""
app/modules/ai_credit_purchases/schemas.py
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# PRICING
# ============================================================================

class CreditPricingResponse(BaseModel):
    price_per_credit: int
    min_purchase: int
    max_purchase: int
    examples: list[dict] = []
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PURCHASE — User (MyCoolPay)
# ============================================================================

class CreditPurchaseRequest(BaseModel):
    credits: int = Field(..., ge=5, le=500)
    payment_method: str = Field(..., description="mobile_money | card")
    phone_number: str | None = None

    @field_validator("payment_method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        if v not in ("mobile_money", "card"):
            raise ValueError("payment_method doit être mobile_money ou card")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str | None, info) -> str | None:
        if info.data.get("payment_method") == "mobile_money" and not v:
            raise ValueError("phone_number requis pour mobile_money")
        return v


class CreditPurchaseResponse(BaseModel):
    payment_id: UUID
    invoice_number: str
    credits: int
    price_per_credit: float
    total_amount: float
    payment_status: str
    ussd: str | None = None
    action: str | None = None
    redirect_url: str | None = None
    transaction_reference: str | None = None
    model_config = ConfigDict(from_attributes=True)


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