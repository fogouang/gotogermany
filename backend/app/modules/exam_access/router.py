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
    UserExamsResponse,
)
from app.modules.exam_access.service import ExamAccessService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


# ── User ─────────────────────────────────────────────────

@router.get("/me", response_model=UserExamsResponse)
async def get_my_exams(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les examens accessibles de l'utilisateur connecté."""
    return await ExamAccessService(db).get_user_exams(current_user.id)


@router.get("/check/{exam_id}", response_model=AccessCheckResponse)
async def check_access(
    exam_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Vérifie si l'utilisateur a accès à un exam.
    Appelé avant le démarrage d'une session.
    """
    return await ExamAccessService(db).check_access(current_user.id, exam_id)


# ── Admin ─────────────────────────────────────────────────

@router.post("/admin/grant", response_model=ExamAccessResponse, status_code=201)
async def admin_grant_access(
    user_id: UUID,
    exam_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """
    Accorde manuellement un accès à un utilisateur — admin uniquement.
    Utile pour les tests et les cas spéciaux.
    """
    return await ExamAccessService(db).grant_admin_access(user_id, exam_id)


@router.delete("/admin/revoke", response_model=SuccessResponse)
async def admin_revoke_access(
    user_id: UUID,
    exam_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Révoque l'accès d'un utilisateur à un exam — admin uniquement."""
    from app.modules.exam_access.repository import ExamAccessRepository
    repo = ExamAccessRepository(db)
    access = await repo.find_by_user_and_exam(user_id, exam_id)
    if not access:
        return SuccessResponse(message="Aucun accès trouvé.")
    await repo.delete(access.id)
    return SuccessResponse(message="Accès révoqué.")


@router.get("/admin/users/{user_id}", response_model=UserExamsResponse)
async def admin_get_user_exams(
    user_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Liste les examens accessibles d'un utilisateur — admin uniquement."""
    return await ExamAccessService(db).get_user_exams(user_id)