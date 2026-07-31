"""
app/modules/enrollments/router.py
"""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.enrollments.dependencies import CenterScope, CurrentCenterScope
from app.modules.enrollments.schemas import (
    CursusCreateRequest, CursusResponse,
    LevelEnrollmentCreateRequest, LevelEnrollmentResponse,
    PaymentCreateRequest, PaymentResponse, BalanceSummaryResponse, RevenueSummaryResponse,
)
from app.modules.enrollments.service import EnrollmentService
from app.modules.auth.dependencies import CurrentCenterStaff, CurrentDirector
from app.shared.database.session import get_db

router = APIRouter()


# ── Cursus ────────────────────────────────

@router.get("/cursus", response_model=list[CursusResponse])
async def list_cursus(
    scope: CurrentCenterScope,
    db: AsyncSession = Depends(get_db),
):
    """Directeur : tous les cursus du centre. Secrétaire : uniquement sa branche."""
    return await EnrollmentService(db).list_cursus_for_staff(scope)


@router.post("/cursus", response_model=CursusResponse)
async def create_cursus(
    data: CursusCreateRequest,
    scope: CurrentCenterScope,
    db: AsyncSession = Depends(get_db),
):
    return await EnrollmentService(db).create_cursus(scope, data)


@router.get("/revenue", response_model=RevenueSummaryResponse)
async def get_revenue_summary(
    current_director: CurrentDirector, db: AsyncSession = Depends(get_db)
):
    """Revenu total encaissé par le centre, ventilé par succursale — vue directeur."""
    return await EnrollmentService(db).get_revenue_summary(current_director.center_id)


# ── Level enrollments ─────────────────────

@router.post("/cursus/{cursus_id}/levels", response_model=LevelEnrollmentResponse)
async def create_level_enrollment(
    cursus_id: UUID,
    data: LevelEnrollmentCreateRequest,
    scope: CurrentCenterScope,
    db: AsyncSession = Depends(get_db),
):
    """Le cursus doit appartenir au périmètre de l'appelant (centre, et branche
    si secrétaire) — vérifié dans EnrollmentService.create_level_enrollment."""
    return await EnrollmentService(db).create_level_enrollment(scope, cursus_id, data)


# ── Paiements ──────────────────────────────

@router.post("/levels/{enrollment_id}/payments", response_model=PaymentResponse)
async def record_payment(
    enrollment_id: UUID,
    data: PaymentCreateRequest,
    scope: CurrentCenterScope,
    current_user: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    """Refuse un paiement de type 'formation' tant que les frais d'inscription
    ne sont pas soldés (règle appliquée dans EnrollmentService.record_payment)."""
    return await EnrollmentService(db).record_payment(scope, enrollment_id, data, current_user)


@router.get("/levels/{enrollment_id}/payments/balance", response_model=BalanceSummaryResponse)
async def get_balance(
    enrollment_id: UUID,
    scope: CurrentCenterScope,
    db: AsyncSession = Depends(get_db),
):
    return await EnrollmentService(db).get_balance_summary(scope, enrollment_id)


@router.get("/levels/{enrollment_id}/payments", response_model=list[PaymentResponse])
async def list_payments(
    enrollment_id: UUID, scope: CurrentCenterScope, db: AsyncSession = Depends(get_db)
):
    """Historique complet des paiements d'un niveau, avec leurs reçus PDF."""
    return await EnrollmentService(db).list_payments_for_enrollment(scope, enrollment_id)