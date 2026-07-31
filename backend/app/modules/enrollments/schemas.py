"""
app/modules/enrollments/schemas.py
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from app.modules.enrollments.models import (
    CursusLevel, CursusStatus, LevelEnrollmentStatus, FormationPaymentType,
)


class CursusCreateRequest(BaseModel):
    student_id: UUID
    branch_id: UUID
    start_level: CursusLevel
    target_level: CursusLevel


    model_config = {"from_attributes": True}

class LevelEnrollmentCreateRequest(BaseModel):
    level: CursusLevel
    inscription_fee_amount: int
    formation_fee_amount: int


class LevelEnrollmentResponse(BaseModel):
    id: UUID
    cursus_id: UUID
    level: CursusLevel
    inscription_fee_amount: int
    formation_fee_amount: int
    status: LevelEnrollmentStatus
    created_at: datetime

    model_config = {"from_attributes": True}

class CursusResponse(BaseModel):
    id: UUID
    student_id: UUID
    branch_id: UUID
    start_level: CursusLevel
    target_level: CursusLevel
    status: CursusStatus
    created_at: datetime
    level_enrollments: list[LevelEnrollmentResponse] = []
    
class PaymentCreateRequest(BaseModel):
    payment_type: FormationPaymentType
    amount: int
    notes: str | None = None


class PaymentResponse(BaseModel):
    id: UUID
    enrollment_id: UUID
    payment_type: FormationPaymentType
    amount: int
    paid_at: datetime
    recorded_by: UUID
    invoice_number: str | None
    invoice_url: str | None = None
    notes: str | None

    model_config = {"from_attributes": True}


class BalanceSummaryResponse(BaseModel):
    inscription_due: int
    inscription_paid: int
    inscription_remaining: int
    formation_due: int
    formation_paid: int
    formation_remaining: int
    status: LevelEnrollmentStatus
    
    
class RevenueSummaryResponse(BaseModel):
    total_revenue: int
    branches_breakdown: dict[str, int]