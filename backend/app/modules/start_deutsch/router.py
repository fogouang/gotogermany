"""
app/modules/start_deutsch/router.py
"""
from uuid import UUID

from fastapi import Depends, File, Form, HTTPException, UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.start_deutsch.schemas import (
    StartDeutschSchreibenCorrectionRequest,
    StartDeutschSchreibenCorrectionResponse,
    StartDeutschSessionCreateRequest,
    StartDeutschSessionListItem,
    StartDeutschSessionResponse,
    StartDeutschSessionResultResponse,
    StartDeutschSessionSubmitRequest,
    StartDeutschSubjectDetail,
    StartDeutschSubjectSummary,
)
from app.modules.start_deutsch.service import (
    StartDeutschCatalogService,
    StartDeutschSchreibenCorrectionService,
    StartDeutschSessionService,
)
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


# ── Catalogue ────────────────────────────────────────────────────

@router.get("/subjects", response_model=list[StartDeutschSubjectSummary])
async def list_subjects(
    _: CurrentUser,
    level: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Catalogue Start Deutsch, accessible à tout étudiant dont le centre a une
    licence active (vérification faite au niveau du middleware/dependency
    d'accès centre, pas ici — à brancher comme pour le reste du catalogue).
    """
    return await StartDeutschCatalogService(db).list_subjects(level)


@router.get("/subjects/{subject_id}", response_model=StartDeutschSubjectDetail)
async def get_subject_detail(
    subject_id: UUID,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Arbre complet Module → Teil → Question (sans correct_answer) pour démarrer une session."""
    return await StartDeutschCatalogService(db).get_subject_detail(subject_id)


# ── Sessions ─────────────────────────────────────────────────────

@router.post("/sessions", response_model=StartDeutschSessionResponse, status_code=201)
async def start_session(
    data: StartDeutschSessionCreateRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await StartDeutschSessionService(db).start_session(user.id, data.subject_id)


@router.post("/sessions/{session_id}/submit", response_model=StartDeutschSessionResponse)
async def submit_session(
    session_id: UUID,
    data: StartDeutschSessionSubmitRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await StartDeutschSessionService(db).submit_session(session_id, user.id, data)


@router.get("/sessions", response_model=list[StartDeutschSessionListItem])
async def list_my_sessions(
    user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await StartDeutschSessionService(db).list_user_sessions(user.id, skip, limit)


@router.get("/sessions/{session_id}/result", response_model=StartDeutschSessionResultResponse)
async def get_session_result(
    session_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await StartDeutschSessionService(db).get_result(session_id, user.id)


# ── Correction Schreiben (IA) ─────────────────────────────────────

@router.post(
    "/sessions/{session_id}/schreiben-correction",
    response_model=StartDeutschSchreibenCorrectionResponse,
    status_code=201,
)
async def correct_schreiben(
    session_id: UUID,
    data: StartDeutschSchreibenCorrectionRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await StartDeutschSchreibenCorrectionService(db).correct(session_id, user.id, data)


# ── Admin — Sujets (liste + suppression) ──────────────────────────

@router.get("/admin/subjects", response_model=list[StartDeutschSubjectSummary])
async def admin_list_subjects(
    _: CurrentAdmin,
    level: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Liste TOUS les sujets (actifs ou non) — vue admin, pour le sélecteur
    audio/images et pour repérer les sujets de test à supprimer."""
    return await StartDeutschCatalogService(db).list_all_admin(level)


@router.delete("/admin/subjects/{subject_id}", response_model=SuccessResponse)
async def admin_delete_subject(
    subject_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Supprime un sujet et tout ce qui en dépend (modules/teile/questions,
    sessions/réponses/corrections) — cascade posée au niveau DB."""
    await StartDeutschCatalogService(db).delete_subject(subject_id)
    return SuccessResponse(message="Sujet supprimé.")


# ── Admin — Import JSON + Audio + Images ──────────────────────────

@router.post("/admin/import", status_code=201)
async def import_subject_json(
    _: CurrentAdmin,
    file: UploadFile = File(..., description="Fichier JSON du sujet Start Deutsch (A1 ou A2)"),
    replace: bool = Form(default=False),
    db: AsyncSession = Depends(get_db),
):
    """
    Importe un sujet Start Deutsch complet depuis un JSON (structure
    level/title/modules[].teile[].questions, cf. import_parsers.py pour le
    détail par format_type). Si replace=true, remplace les questions des
    Teile déjà existants.
    """
    from app.modules.start_deutsch.import_service import StartDeutschImportService

    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un JSON.")
    json_bytes = await file.read()
    return await StartDeutschImportService(db).import_from_json(json_bytes, replace=replace)


@router.post("/admin/audio")
async def import_subject_audio(
    _: CurrentAdmin,
    subject_id: UUID = Form(..., description="ID du sujet Start Deutsch ciblé (cf. GET /subjects)"),
    files: list[UploadFile] = File(..., description="Fichiers MP3 — convention hoeren_teilN.mp3"),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.start_deutsch.import_service import StartDeutschImportService

    mp3_files = [f for f in files if f.filename and f.filename.lower().endswith(".mp3")]
    if not mp3_files:
        raise HTTPException(status_code=400, detail="Aucun fichier MP3 trouvé.")
    return await StartDeutschImportService(db).import_audio_files(subject_id=subject_id, files=mp3_files)


@router.post("/admin/images")
async def import_subject_images(
    _: CurrentAdmin,
    subject_id: UUID = Form(..., description="ID du sujet Start Deutsch ciblé (cf. GET /subjects)"),
    files: list[UploadFile] = File(..., description="Images PNG/JPG/WebP"),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.start_deutsch.import_service import StartDeutschImportService

    img_files = [
        f for f in files
        if f.filename and f.filename.lower().rsplit(".", 1)[-1] in ("png", "jpg", "jpeg", "webp")
    ]
    if not img_files:
        raise HTTPException(status_code=400, detail="Aucun fichier image trouvé.")
    return await StartDeutschImportService(db).import_images(subject_id=subject_id, files=img_files)