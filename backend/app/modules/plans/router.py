"""
app/modules/plans/router.py
"""
from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin
from app.modules.plans.schemas import PlanCreate, PlanResponse, PlanUpdate
from app.modules.plans.service import PlanService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


# ── Public ────────────────────────────────────────────

@router.get("", response_model=list[PlanResponse])
async def get_plans(db: AsyncSession = Depends(get_db)):
    """Liste les plans actifs — accessible sans auth pour la page tarifs."""
    return await PlanService(db).get_active_plans()


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: UUID, db: AsyncSession = Depends(get_db)):
    return await PlanService(db).get_by_id(plan_id)


# ── Admin ─────────────────────────────────────────────

@router.post("", response_model=PlanResponse, status_code=201)
async def create_plan(
    data: PlanCreate,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await PlanService(db).create(data)


@router.patch("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: UUID,
    data: PlanUpdate,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await PlanService(db).update(plan_id, data)


@router.delete("/{plan_id}", response_model=SuccessResponse)
async def delete_plan(
    plan_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await PlanService(db).delete(plan_id)
    return SuccessResponse(message="Plan supprimé.")