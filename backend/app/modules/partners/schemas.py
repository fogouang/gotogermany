"""
app/modules/partners/schemas.py
"""
import uuid
from datetime import datetime
from pydantic import EmailStr, Field
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Requests
# ─────────────────────────────────────────────

class PartnerCreateRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=150)
    contact_email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    notes: str | None = None


class PartnerUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    contact_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    notes: str | None = None
    is_active: bool | None = None


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────

class PartnerResponse(BaseSchema):
    id: uuid.UUID
    name: str
    contact_email: str
    phone: str | None
    is_active: bool
    created_at: datetime


class PartnerDetailResponse(PartnerResponse):
    """Réponse étendue avec notes internes — admin uniquement."""
    notes: str | None
    updated_at: datetime


class PartnerStatsResponse(BaseSchema):
    """Stats d'un partenaire pour le dashboard admin."""
    partner_id: uuid.UUID
    partner_name: str
    total_codes: int
    active_codes: int
    total_uses: int
    total_commission_due: float  # somme des commissions générées