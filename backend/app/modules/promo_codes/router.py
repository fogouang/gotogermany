"""
app/modules/promo_codes/router.py
"""
from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.promo_codes.schemas import (
    PromoCodeCreateRequest,
    PromoCodeResponse,
    PromoCodeUpdateRequest,
    PromoCodeValidateRequest,
    PromoCodeValidateResponse,
)
from app.modules.promo_codes.service import PromoCodeService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


# ── Public — validation avant paiement ───────────────────

@router.post("/validate", response_model=PromoCodeValidateResponse)
async def validate_promo_code(
    data: PromoCodeValidateRequest,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Valide un code promo et retourne la réduction applicable.
    Appelé depuis le frontend avant de confirmer le paiement.
    """
    return await PromoCodeService(db).validate(data.code, data.exam_id)


# ── Admin — CRUD ──────────────────────────────────────────

@router.get("", response_model=list[PromoCodeResponse])
async def list_promo_codes(
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les codes promo — admin uniquement."""
    return await PromoCodeService(db).get_all()


@router.get("/{code_id}", response_model=PromoCodeResponse)
async def get_promo_code(
    code_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await PromoCodeService(db).get_by_id(code_id)


@router.post("", response_model=PromoCodeResponse, status_code=201)
async def create_promo_code(
    data: PromoCodeCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await PromoCodeService(db).create(data)


@router.patch("/{code_id}", response_model=PromoCodeResponse)
async def update_promo_code(
    code_id: UUID,
    data: PromoCodeUpdateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await PromoCodeService(db).update(code_id, data)


@router.delete("/{code_id}", response_model=SuccessResponse)
async def delete_promo_code(
    code_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await PromoCodeService(db).delete(code_id)
    return SuccessResponse(message="Code promo supprimé.")