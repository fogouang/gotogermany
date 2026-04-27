"""
app/modules/promo_codes/schemas.py
"""
import uuid
from datetime import datetime
from typing import Literal
from pydantic import Field, model_validator
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Requests
# ─────────────────────────────────────────────

class PromoCodeCreateRequest(BaseSchema):
    partner_id: uuid.UUID | None = None  # NULL = promo interne sans commission
    code: str = Field(min_length=3, max_length=50, pattern=r"^[A-Z0-9_\-]+$")
    discount_type: Literal["percent", "fixed"]
    discount_value: int = Field(gt=0)
    commission_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    max_uses: int | None = Field(default=None, gt=0)
    expires_at: datetime | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def validate_percent_max(self) -> "PromoCodeCreateRequest":
        if self.discount_type == "percent" and self.discount_value > 100:
            raise ValueError("discount_value ne peut pas dépasser 100 pour un type 'percent'.")
        return self

    @model_validator(mode="after")
    def validate_commission_requires_partner(self) -> "PromoCodeCreateRequest":
        if self.commission_rate > 0 and self.partner_id is None:
            raise ValueError("commission_rate > 0 nécessite un partner_id.")
        return self


class PromoCodeUpdateRequest(BaseSchema):
    is_active: bool | None = None
    max_uses: int | None = Field(default=None, gt=0)
    expires_at: datetime | None = None
    commission_rate: float | None = Field(default=None, ge=0.0, le=100.0)


class PromoCodeValidateRequest(BaseSchema):
    """Vérifie un code avant paiement et retourne la réduction applicable."""
    code: str
    exam_id: uuid.UUID  # pour calculer la réduction sur le bon montant


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────

class PromoCodeResponse(BaseSchema):
    id: uuid.UUID
    code: str
    discount_type: str
    discount_value: int
    commission_rate: float
    max_uses: int | None
    used_count: int
    expires_at: datetime | None
    is_active: bool
    partner_id: uuid.UUID | None
    created_at: datetime


class PromoCodeValidateResponse(BaseSchema):
    """Réponse à la validation d'un code promo avant paiement."""
    code: str
    is_valid: bool
    discount_type: str | None = None
    discount_value: int | None = None
    amount_gross: int | None = None   # prix original de l'exam
    amount_paid: int | None = None    # prix après réduction
    discount_amount: int | None = None
    message: str  # "Code valide", "Code expiré", "Code épuisé", etc.