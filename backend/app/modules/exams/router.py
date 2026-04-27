"""
app/modules/exams/router.py
"""
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.exams.schemas import (
    ExamCatalogResponse, ExamDetailResponse, ExamListResponse,
    ExamCreateRequest, ExamUpdateRequest,
    LevelCreateRequest, LevelUpdateRequest, LevelResponse,
    SubjectCreateRequest, SubjectResponse,
    ModuleCreateRequest, ModuleResponse, SubjectUpdateRequest,
    TeilCreateRequest, TeilResponse,
)
from app.modules.exams.service import ExamService
from app.modules.exam_access.service import ExamAccessService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


# ── Catalogue public ─────────────────────────────────────

@router.get("", response_model=list[ExamCatalogResponse])
async def get_catalog(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    exams = await ExamService(db).get_catalog()
    return await ExamAccessService(db).enrich_catalog(exams, current_user.id)


@router.get("/{exam_id}", response_model=ExamDetailResponse)
async def get_exam_detail(
    exam_id: UUID,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).get_detail(exam_id)


@router.get("/slug/{slug}", response_model=ExamDetailResponse)
async def get_exam_by_slug(
    slug: str,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).get_by_slug(slug)


# ── Admin — Exams CRUD ───────────────────────────────────

@router.post("", response_model=ExamListResponse, status_code=201)
async def create_exam(
    data: ExamCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).create(data)


@router.patch("/{exam_id}", response_model=ExamListResponse)
async def update_exam(
    exam_id: UUID,
    data: ExamUpdateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).update(exam_id, data)


@router.delete("/{exam_id}", response_model=SuccessResponse)
async def delete_exam(
    exam_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await ExamService(db).delete(exam_id)
    return SuccessResponse(message="Exam supprimé.")


# ── Admin — Levels ───────────────────────────────────────

@router.get("/{exam_id}/levels", response_model=list[LevelResponse])
async def get_levels(
    exam_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).get_levels(exam_id)


@router.post("/{exam_id}/levels", response_model=LevelResponse, status_code=201)
async def create_level(
    exam_id: UUID,
    data: LevelCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).create_level(exam_id, data)


@router.patch("/levels/{level_id}", response_model=LevelResponse)
async def update_level(
    level_id: UUID,
    data: LevelUpdateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).update_level(level_id, data)


@router.delete("/levels/{level_id}", response_model=SuccessResponse)
async def delete_level(
    level_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await ExamService(db).delete_level(level_id)
    return SuccessResponse(message="Level supprimé.")


# ── Admin — Subjects ─────────────────────────────────────

@router.get("/levels/{level_id}/subjects", response_model=list[SubjectResponse])
async def get_subjects(
    level_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Liste les sujets d'un level."""
    return await ExamService(db).get_subjects(level_id)


@router.post("/levels/{level_id}/subjects", response_model=SubjectResponse, status_code=201)
async def create_subject(
    level_id: UUID,
    data: SubjectCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Crée un nouveau sujet — subject_number auto-incrémenté."""
    return await ExamService(db).create_subject(level_id, data)


@router.delete("/subjects/{subject_id}", response_model=SuccessResponse)
async def delete_subject(
    subject_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await ExamService(db).delete_subject(subject_id)
    return SuccessResponse(message="Sujet supprimé.")


# ── Admin — Modules ──────────────────────────────────────
# Module appartient maintenant à subject_id (pas level_id)

@router.post("/subjects/{subject_id}/modules", response_model=ModuleResponse, status_code=201)
async def create_module(
    subject_id: UUID,
    data: ModuleCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).create_module(subject_id, data)


@router.delete("/modules/{module_id}", response_model=SuccessResponse)
async def delete_module(
    module_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await ExamService(db).delete_module(module_id)
    return SuccessResponse(message="Module supprimé.")


# ── Admin — Teile ────────────────────────────────────────

@router.post("/modules/{module_id}/teile", response_model=TeilResponse, status_code=201)
async def create_teil(
    module_id: UUID,
    data: TeilCreateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).create_teil(module_id, data)


@router.delete("/teile/{teil_id}", response_model=SuccessResponse)
async def delete_teil(
    teil_id: UUID,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await ExamService(db).delete_teil(teil_id)
    return SuccessResponse(message="Teil supprimé.")


# ── Admin — Import JSON + Audio ──────────────────────────

from fastapi import UploadFile, File, Form

@router.post("/admin/import", status_code=201)
async def import_exam_json(
    _: CurrentAdmin,
    file: UploadFile = File(..., description="Fichier JSON de l'examen"),
    replace: bool = Form(default=False),
    db: AsyncSession = Depends(get_db),
):
    """
    Importe un examen complet depuis un fichier JSON.
    Le JSON est celui généré par generate_telc_b1.py ou generate_exam.py.
    Si replace=true, supprime et réinsère les questions existantes.
    """
    from app.modules.exams.import_service import ExamImportService
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un JSON.")
    json_bytes = await file.read()
    return await ExamImportService(db).import_from_json(json_bytes, replace=replace)


@router.post("/admin/{exam_id}/audio")
async def import_exam_audio(
    _: CurrentAdmin,
    exam_id: UUID,
    files: list[UploadFile] = File(..., description="Fichiers MP3 du dossier audio généré"),
    subject_number: int = Form(..., description="Numéro du sujet (1, 2, 3...)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Associe plusieurs fichiers MP3 aux questions d'un sujet.
    Sélectionner tous les MP3 du dossier audio_telc_YYYYMMDD correspondant.
    Convention : horen_teil1_audio1.mp3, horen_teil2.mp3, horen_teil3_audio1.mp3...
    """
    from app.modules.exams.import_service import ExamImportService
    mp3_files = [f for f in files if f.filename and f.filename.lower().endswith(".mp3")]
    if not mp3_files:
        raise HTTPException(status_code=400, detail="Aucun fichier MP3 trouvé.")
    return await ExamImportService(db).import_audio_files(
        exam_id=exam_id,
        files=mp3_files,
        subject_number=subject_number,
    )
    
@router.patch("/subjects/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: UUID,
    data: SubjectUpdateRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await ExamService(db).update_subject(subject_id, data)