"""
app/modules/partners/router.py
"""
from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin
from app.modules.partners.schemas import (
    PartnerCreateRequest,
    PartnerDetailResponse,
    PartnerStatsResponse,
    PartnerUpdateRequest,
)
from app.modules.partners.service import PartnerService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


@router.get("", response_model=list[PartnerDetailResponse])
async def list_partners(
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les partenaires — admin uniquement."""
    return await PartnerService(db).get_all()


@router.get("/{partner_id}", response_model=PartnerDetailResponse)
async def get_partner(
    partner_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await PartnerService(db).get_by_id(partner_id)


@router.get("/{partner_id}/stats", response_model=PartnerStatsResponse)
async def get_partner_stats(
    partner_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Stats codes + utilisations + commissions dues."""
    return await PartnerService(db).get_stats(partner_id)


@router.post("", response_model=PartnerDetailResponse, status_code=201)
async def create_partner(
    data: PartnerCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await PartnerService(db).create(data)


@router.patch("/{partner_id}", response_model=PartnerDetailResponse)
async def update_partner(
    partner_id: UUID,
    data: PartnerUpdateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await PartnerService(db).update(partner_id, data)


@router.delete("/{partner_id}", response_model=SuccessResponse)
async def delete_partner(
    partner_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await PartnerService(db).delete(partner_id)
    return SuccessResponse(message="Partenaire supprimé.")