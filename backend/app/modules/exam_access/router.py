"""
app/modules/exam_access/router.py
"""
from uuid import UUID
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.exam_access.schemas import (
    AccessCheckResponse,
    ExamAccessResponse,
    UserLevelsResponse,
)
from app.modules.exam_access.service import ExamAccessService
from app.modules.exam_access.repository import ExamAccessRepository
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()

# ── User ─────────────────────────────────────────────────

@router.get("/me", response_model=UserLevelsResponse)
async def get_my_levels(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les levels accessibles de l'utilisateur connecté."""
    return await ExamAccessService(db).get_user_levels(current_user.id)


@router.get("/check/{level_id}", response_model=AccessCheckResponse)
async def check_access(
    level_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Vérifie si l'utilisateur a accès à un level.
    Appelé avant le démarrage d'une session.
    """
    return await ExamAccessService(db).check_level_access(current_user.id, level_id)


# ── Admin ─────────────────────────────────────────────────

@router.post("/admin/grant", response_model=ExamAccessResponse, status_code=201)
async def admin_grant_access(
    user_id: UUID,
    level_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Accorde manuellement un accès à un level — admin uniquement."""
    return await ExamAccessService(db).grant_admin_access(user_id, level_id)


@router.delete("/admin/revoke", response_model=SuccessResponse)
async def admin_revoke_access(
    user_id: UUID,
    level_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Révoque l'accès d'un utilisateur à un level — admin uniquement."""
    repo = ExamAccessRepository(db)
    access = await repo.find_by_user_and_level(user_id, level_id)
    if not access:
        return SuccessResponse(message="Aucun accès trouvé.")
    await repo.delete(access.id)
    return SuccessResponse(message="Accès révoqué.")


@router.get("/admin/users/{user_id}", response_model=UserLevelsResponse)
async def admin_get_user_levels(
    user_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Liste les levels accessibles d'un utilisateur — admin uniquement."""
    return await ExamAccessService(db).get_user_levels(user_id)


@router.post("/admin/grant-all/{user_id}", response_model=SuccessResponse)
async def admin_grant_all_levels(
    user_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """
    Donne accès à tous les levels actifs à un user.
    Utile pour les tests ou les cas spéciaux.
    """
    from app.modules.exams.repository import LevelRepository
    from app.modules.exam_access.models import ExamAccess
    from datetime import datetime, timezone

    repo = ExamAccessRepository(db)
    levels = await LevelRepository(db).get_all_active()
    count = 0

    for level in levels:
        existing = await repo.find_by_user_and_level(user_id, level.id)
        if not existing:
            db.add(ExamAccess(
                user_id=user_id,
                level_id=level.id,
                access_type="paid",
                payment_id=None,
                expires_at=None,
                granted_at=datetime.now(timezone.utc),
            ))
            count += 1

    await db.commit()
    return SuccessResponse(message=f"{count} accès accordés.")