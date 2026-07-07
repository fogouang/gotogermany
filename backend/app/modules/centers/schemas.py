"""
app/modules/centers/schemas.py
"""
import uuid
from datetime import datetime
from pydantic import Field, field_validator
from app.shared.schemas.base import BaseSchema
from app.modules.centers.models import LicenseStatus, PaymentMethod


# ─────────────────────────────────────────────
# Requests
# ─────────────────────────────────────────────
class CenterCreateRequest(BaseSchema):
    """Création d'un centre — admin ITIA uniquement."""
    name: str = Field(min_length=2, max_length=255)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=20)

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class BranchCreateRequest(BaseSchema):
    """Création d'une succursale — admin ITIA (initiale) ou directeur (supplémentaire)."""
    name: str = Field(min_length=2, max_length=255)
    is_main: bool = False

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class LicenseFormulaCreateRequest(BaseSchema):
    """Création d'une formule de licence — admin ITIA uniquement."""
    label: str = Field(min_length=2, max_length=100)
    duration_months: int = Field(gt=0, le=24)
    max_students: int = Field(gt=0)


class CenterLicenseActivateRequest(BaseSchema):
    """Activation d'une licence pour un centre — admin ITIA uniquement."""
    formula_id: uuid.UUID
    payment_method: PaymentMethod
    payment_reference: str | None = Field(default=None, max_length=255)


class CenterLicenseExtendRequest(BaseSchema):
    """Extension du quota d'une licence active — admin ITIA uniquement."""
    additional_students: int = Field(gt=0)
    payment_method: PaymentMethod
    payment_reference: str | None = Field(default=None, max_length=255)


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────
class LicenseFormulaResponse(BaseSchema):
    id: uuid.UUID
    label: str
    duration_months: int
    max_students: int
    is_active: bool


class CenterLicenseResponse(BaseSchema):
    id: uuid.UUID
    center_id: uuid.UUID
    formula_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    max_students: int
    status: LicenseStatus
    payment_method: PaymentMethod | None
    payment_reference: str | None
    created_at: datetime


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
    created_at: datetime


class CenterDetailResponse(CenterResponse):
    branches: list[BranchResponse] = []
    active_license: CenterLicenseResponse | None = None


class LicenseUsageResponse(BaseSchema):
    """Vue consolidée pour le panel directeur."""
    license: CenterLicenseResponse | None
    formula_label: str | None          
    students_used: int
    students_remaining: int
    days_remaining: int | None
    branches_breakdown: dict[str, int]  