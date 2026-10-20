"""
app/modules/sales/router.py
"""
from typing import Literal
from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.sales.schemas import (
    ActivationRequest,
    ActivationResponse,
    CommissionRuleCreate,
    CommissionRuleResponse,
    CommissionRuleUpdate,
    PartnerSaleResponse,
    PartnerSettingsUpdate,
    PartnerSummaryResponse,
    SettlementCreate,
    SettlementResponse,
    PlatformRevenueResponse
)
from app.modules.sales.service import SalesService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()

PartnerTypePath = Literal["center", "ambassador"]


# ── Partenaire connecté (centre ou ambassadeur) ──────────

@router.post("/activations", response_model=ActivationResponse, status_code=201)
async def activate_account(
    data: ActivationRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Active le compte d'un élève (encaissé par le partenaire) et enregistre la vente."""
    return await SalesService(db).activate(current_user, data)


@router.get("/me/summary", response_model=PartnerSummaryResponse)
async def my_summary(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SalesService(db)
    return await service.summary(await service.partner_for_actor(current_user))


@router.get("/me/sales", response_model=list[PartnerSaleResponse])
async def my_sales(
    current_user: CurrentUser,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    service = SalesService(db)
    partner = await service.partner_for_actor(current_user)
    return await service.list_sales(partner, limit=limit, offset=offset)


@router.get("/me/settlements", response_model=list[SettlementResponse])
async def my_settlements(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SalesService(db)
    return await service.list_settlements(await service.partner_for_actor(current_user))


# ── Admin : règles de commission ─────────────────────────

@router.get("/admin/commission-rules", response_model=list[CommissionRuleResponse])
async def list_rules(_: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    return await SalesService(db).list_rules()


@router.post("/admin/commission-rules", response_model=CommissionRuleResponse, status_code=201)
async def create_rule(data: CommissionRuleCreate, _: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    return await SalesService(db).create_rule(data)


@router.patch("/admin/commission-rules/{rule_id}", response_model=CommissionRuleResponse)
async def update_rule(
    rule_id: UUID, data: CommissionRuleUpdate, _: CurrentAdmin, db: AsyncSession = Depends(get_db)
):
    return await SalesService(db).update_rule(rule_id, data)


@router.delete("/admin/commission-rules/{rule_id}", response_model=SuccessResponse)
async def delete_rule(rule_id: UUID, _: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    await SalesService(db).delete_rule(rule_id)
    return SuccessResponse(message="Règle supprimée.")

@router.get("/admin/revenue", response_model=PlatformRevenueResponse)
async def platform_revenue(_: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    """[Admin] Chiffre de la plateforme, total et mois en cours."""
    return await SalesService(db).platform_revenue()

# ── Admin : partenaires ──────────────────────────────────

@router.get("/admin/partners", response_model=list[PartnerSummaryResponse])
async def partners_overview(_: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    """Tous les centres et ambassadeurs avec leur solde et leur statut de blocage."""
    return await SalesService(db).admin_overview()


@router.get("/admin/partners/{partner_type}/{partner_id}", response_model=PartnerSummaryResponse)
async def partner_summary(
    partner_type: PartnerTypePath, partner_id: UUID, _: CurrentAdmin, db: AsyncSession = Depends(get_db)
):
    service = SalesService(db)
    return await service.summary(await service.get_partner(partner_type, partner_id))


@router.get("/admin/partners/{partner_type}/{partner_id}/sales", response_model=list[PartnerSaleResponse])
async def partner_sales(
    partner_type: PartnerTypePath,
    partner_id: UUID,
    _: CurrentAdmin,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    service = SalesService(db)
    partner = await service.get_partner(partner_type, partner_id)
    return await service.list_sales(partner, limit=limit, offset=offset)


@router.get(
    "/admin/partners/{partner_type}/{partner_id}/settlements",
    response_model=list[SettlementResponse],
)
async def partner_settlements(
    partner_type: PartnerTypePath, partner_id: UUID, _: CurrentAdmin, db: AsyncSession = Depends(get_db)
):
    service = SalesService(db)
    return await service.list_settlements(await service.get_partner(partner_type, partner_id))


@router.patch(
    "/admin/partners/{partner_type}/{partner_id}/settings",
    response_model=PartnerSummaryResponse,
)
async def update_partner_settings(
    partner_type: PartnerTypePath,
    partner_id: UUID,
    data: PartnerSettingsUpdate,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await SalesService(db).update_partner_settings(partner_type, partner_id, data)


# ── Admin : règlements ───────────────────────────────────

@router.post("/admin/settlements", response_model=SettlementResponse, status_code=201)
async def create_settlement(
    data: SettlementCreate, current_admin: CurrentAdmin, db: AsyncSession = Depends(get_db)
):
    """Enregistre un règlement et l'impute sur les ventes les plus anciennes."""
    return await SalesService(db).create_settlement(current_admin, data)