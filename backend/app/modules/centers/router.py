"""
app/modules/centers/router.py
"""
from uuid import UUID
from fastapi import Depends, File, UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentDirector, CurrentCenterStaff
from app.modules.centers.schemas import (
    CenterCreateRequest,
    CenterResponse,
    BranchCreateRequest,
    BranchResponse,
    CenterUpdateRequest,
    CenterCreditPoolRechargeRequest,
    CenterDefaultCreditsUpdateRequest,
    CenterCreditTransactionResponse,
    CenterPoolResponse,
)
from app.modules.centers.service import CenterService
from app.shared.database.session import get_db
from app.shared.exceptions.http import BadRequestException

router = APIRouter()


# ── Directeur (routes /me/... déclarées avant /{center_id}/...) ──

@router.get("/me", response_model=CenterResponse)
async def get_my_center(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).center_repo.get_by_id_or_404(current_director.center_id)


@router.get("/me/branches", response_model=list[BranchResponse])
async def list_my_branches(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).list_my_branches(current_director.center_id)


@router.post("/me/branches", response_model=BranchResponse, status_code=201)
async def create_my_branch(
    data: BranchCreateRequest,
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).create_branch(current_director.center_id, data)


@router.get("/me/pool", response_model=CenterPoolResponse)
async def get_my_center_pool(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).center_repo.get_by_id_or_404(current_director.center_id)


@router.patch("/me/default-credits", response_model=CenterPoolResponse)
async def update_default_credits(
    data: CenterDefaultCreditsUpdateRequest,
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).update_default_credits(
        current_director.center_id, data.default_credits_per_student, current_director
    )


@router.get("/me/credit-transactions", response_model=list[CenterCreditTransactionResponse])
async def get_my_center_credit_transactions(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).get_credit_transactions_for_director(
        current_director.center_id
    )


@router.get("/me/credit-transactions/mine", response_model=list[CenterCreditTransactionResponse])
async def get_my_credit_transactions(
    current_user: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).get_credit_transactions_for_secretary(current_user)


@router.patch("/me", response_model=CenterResponse)
async def update_my_center(
    data: CenterUpdateRequest,
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).update_my_center(current_director.center_id, data)


@router.post("/me/logo", response_model=CenterResponse)
async def upload_my_logo(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
):
    """Upload du logo du centre, affiché en en-tête des reçus PDF."""
    from pathlib import Path

    allowed_ext = {".png", ".jpg", ".jpeg"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_ext:
        raise BadRequestException(detail="Format non supporté (PNG/JPG uniquement).")

    logos_dir = Path("storage/center_logos")
    logos_dir.mkdir(parents=True, exist_ok=True)

    file_path = logos_dir / f"{current_director.center_id}{ext}"
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return await CenterService(db).update_my_logo(current_director.center_id, str(file_path))


# ── Admin ─────────────────────────────────────

@router.post("", response_model=CenterResponse, status_code=201)
async def create_center(
    data: CenterCreateRequest,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Créer un centre (crée aussi sa succursale principale)."""
    return await CenterService(db).create_center(data)


@router.get("", response_model=list[CenterResponse])
async def list_centers(
    skip: int = 0,
    limit: int = 100,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).list_centers(skip=skip, limit=limit)


@router.post("/{center_id}/branches", response_model=BranchResponse, status_code=201)
async def create_branch(
    center_id: UUID,
    data: BranchCreateRequest,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).create_branch(center_id, data)


@router.patch("/{center_id}/toggle-active", response_model=CenterResponse)
async def toggle_center_active(
    center_id: UUID,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).toggle_active(center_id)


@router.post("/{center_id}/credit-pool/recharge", response_model=CenterPoolResponse)
async def recharge_credit_pool(
    center_id: UUID,
    data: CenterCreditPoolRechargeRequest,
    current_admin: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await CenterService(db).recharge_pool(
        center_id, data.amount, current_admin, data.reason
    )