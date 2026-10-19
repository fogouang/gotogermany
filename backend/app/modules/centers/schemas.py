"""
app/modules/centers/schemas.py
"""
import uuid
from datetime import datetime
from pydantic import Field, field_validator
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Requests
# ─────────────────────────────────────────────
class CenterCreateRequest(BaseSchema):
    """Création d'un centre : admin uniquement."""
    name: str = Field(min_length=2, max_length=255)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=20)

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class BranchCreateRequest(BaseSchema):
    """Création d'une succursale : admin (initiale) ou directeur (supplémentaire)."""
    name: str = Field(min_length=2, max_length=255)
    is_main: bool = False

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class CenterCreditPoolRechargeRequest(BaseSchema):
    """Rechargement manuel du pool : admin uniquement."""
    amount: int = Field(gt=0)
    reason: str | None = Field(default=None, max_length=255)


class CenterDefaultCreditsUpdateRequest(BaseSchema):
    """Le directeur ajuste le nombre de crédits par défaut à la création d'un étudiant."""
    default_credits_per_student: int = Field(ge=0, le=100)


class CenterUpdateRequest(BaseSchema):
    address: str | None = Field(default=None, max_length=255)


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────
class BranchResponse(BaseSchema):
    id: uuid.UUID
    center_id: uuid.UUID
    name: str
    is_main: bool
    created_at: datetime


class CenterResponse(BaseSchema):
    id: uuid.UUID
    name: str
    contact_email: str | None
    contact_phone: str | None
    is_active: bool
    address: str | None = None
    logo_path: str | None = None
    ai_credit_pool_balance: int
    default_credits_per_student: int
    # Partenariat (ventes)
    partner_can_activate: bool = True
    partner_unpaid_limit: int | None = None
    partner_payment_delay_hours: int = 24
    created_at: datetime


class CenterDetailResponse(CenterResponse):
    branches: list[BranchResponse] = []


class CenterCreditTransactionResponse(BaseSchema):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    performed_by: uuid.UUID
    performer_name: str
    amount: int
    pool_balance_after: int
    reason: str | None
    created_at: datetime


class CenterPoolResponse(BaseSchema):
    ai_credit_pool_balance: int
    default_credits_per_student: int
    
    
# ─────────────────────────────────────────────
# Lien d'inscription des élèves
# ─────────────────────────────────────────────
class JoinBranchOption(BaseSchema):
    id: uuid.UUID
    name: str


class JoinInfoResponse(BaseSchema):
    """Page publique /rejoindre/{token} : nom du centre et succursales."""
    center_name: str
    branches: list[JoinBranchOption]


class JoinLinkResponse(BaseSchema):
    token: str
    enabled: bool
    center_name: str


class JoinLinkUpdateRequest(BaseSchema):
    enabled: bool