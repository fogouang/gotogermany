"""
app/modules/questions/router.py
"""
from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.questions.schemas import (
    BulkQuestionCreateRequest,
    QuestionAdminResponse,
    QuestionCreateRequest,
    QuestionResponse,
    QuestionUpdateRequest,
)
from app.modules.questions.service import QuestionService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


# ── Vue étudiant — sans correct_answer ───────────────────

@router.get("/teile/{teil_id}/questions", response_model=list[QuestionResponse])
async def get_questions_by_teil(
    teil_id: UUID,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Questions d'un Teil — vue étudiant, sans correct_answer.
    En pratique, le frontend les reçoit via SessionStartResponse,
    cet endpoint est utile pour preview ou débogage.
    """
    return await QuestionService(db).get_by_teil(teil_id)


# ── Admin — avec correct_answer ───────────────────────────

@router.get(
    "/admin/teile/{teil_id}/questions",
    response_model=list[QuestionAdminResponse],
)
async def admin_get_questions(
    teil_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Liste toutes les questions d'un Teil avec correct_answer — admin."""
    return await QuestionService(db).get_by_teil(teil_id)


@router.get(
    "/admin/questions/{question_id}",
    response_model=QuestionAdminResponse,
)
async def admin_get_question(
    question_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await QuestionService(db).get_by_id(question_id)


@router.post(
    "/admin/teile/{teil_id}/questions",
    response_model=QuestionAdminResponse,
    status_code=201,
)
async def create_question(
    teil_id: UUID,
    data: QuestionCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await QuestionService(db).create(teil_id, data)


@router.post(
    "/admin/teile/{teil_id}/questions/bulk",
    response_model=list[QuestionAdminResponse],
    status_code=201,
)
async def bulk_create_questions(
    teil_id: UUID,
    data: BulkQuestionCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Insert en masse — utilisé par le script d'import."""
    return await QuestionService(db).bulk_create(teil_id, data)


@router.put(
    "/admin/teile/{teil_id}/questions/replace",
    response_model=list[QuestionAdminResponse],
)
async def replace_questions(
    teil_id: UUID,
    data: BulkQuestionCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """
    Remplace toutes les questions d'un Teil.
    Utile pour re-importer sans conflit.
    """
    return await QuestionService(db).replace_teil_questions(teil_id, data)


@router.patch(
    "/admin/questions/{question_id}",
    response_model=QuestionAdminResponse,
)
async def update_question(
    question_id: UUID,
    data: QuestionUpdateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await QuestionService(db).update(question_id, data)


@router.delete(
    "/admin/questions/{question_id}",
    response_model=SuccessResponse,
)
async def delete_question(
    question_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await QuestionService(db).delete(question_id)
    return SuccessResponse(message="Question supprimée.")