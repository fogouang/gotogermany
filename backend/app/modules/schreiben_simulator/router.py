"""
app/modules/schreiben_simulator/router.py
"""
from uuid import UUID

from fastapi import Depends, HTTPException, Query
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.schreiben_simulator.schemas import (
    SchreibenSubjectCreate,
    SchreibenSubjectUpdate,
    SchreibenSubjectResponse,
    SimulatorCorrectRequest,
    SimulatorCorrectResponse,
    SimulatorResultResponse,
)
from app.modules.schreiben_simulator.service import SchreibenSimulatorService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


# ── Lecture publique ─────────────────────────────────────

@router.get("", response_model=list[SchreibenSubjectResponse])
async def list_subjects(
    _: CurrentUser,
    provider: str | None = Query(default=None, description="Filtrer par provider (telc, goethe, osd)"),
    level: str | None = Query(default=None, description="Filtrer par niveau (b1, b2)"),
    db: AsyncSession = Depends(get_db),
):
    """Liste les sujets simulateur actifs, avec filtres optionnels."""
    return await SchreibenSimulatorService(db).list_subjects(
        provider=provider,
        level=level,
        active_only=True,
    )


@router.get("/{subject_id}", response_model=SchreibenSubjectResponse)
async def get_subject(
    subject_id: UUID,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Récupère un sujet simulateur par son ID."""
    try:
        return await SchreibenSimulatorService(db).get_subject(subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Correction simulateur ────────────────────────────────

@router.post("/correct", response_model=SimulatorCorrectResponse)
async def correct_submission(
    request: SimulatorCorrectRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Lance la correction IA d'un sujet simulateur.
    Le candidat envoie subject_id + ses textes rédigés (task_texts).
    """
    try:
        return await SchreibenSimulatorService(db).correct(request,user_id=current_user.id,)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my/results", response_model=list[SimulatorResultResponse])
async def my_results(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Historique des corrections simulateur de l'utilisateur connecté."""
    return await SchreibenSimulatorService(db).list_my_results(current_user.id)

# ── Admin CRUD ───────────────────────────────────────────

@router.get("/admin/all", response_model=list[SchreibenSubjectResponse])
async def list_all_subjects(
    _: CurrentAdmin,
    provider: str | None = Query(default=None),
    level: str | None = Query(default=None),
    active_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    """Admin : liste tous les sujets (y compris inactifs)."""
    return await SchreibenSimulatorService(db).list_subjects(
        provider=provider,
        level=level,
        active_only=active_only,
    )


@router.post("", response_model=SchreibenSubjectResponse, status_code=201)
async def create_subject(
    data: SchreibenSubjectCreate,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Admin : crée un nouveau sujet simulateur."""
    try:
        return await SchreibenSimulatorService(db).create_subject(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




@router.patch("/{subject_id}", response_model=SchreibenSubjectResponse)
async def update_subject(
    subject_id: UUID,
    data: SchreibenSubjectUpdate,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Admin : met à jour un sujet simulateur."""
    try:
        return await SchreibenSimulatorService(db).update_subject(subject_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{subject_id}", response_model=SuccessResponse)
async def delete_subject(
    subject_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Admin : supprime un sujet simulateur."""
    try:
        await SchreibenSimulatorService(db).delete_subject(subject_id)
        return SuccessResponse(message="Sujet supprimé.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))