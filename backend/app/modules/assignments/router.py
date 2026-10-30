"""
app/modules/assignments/router.py
"""
from uuid import UUID

from fastapi import Depends, File, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assignments.schemas import (
    AssignmentCreate,
    AssignmentDetailResponse,
    AssignmentSummaryResponse,
    BankSubjectResponse,
    GradeRequest,
    StudentAssignmentResponse,
    SubmissionGradingResponse,
)
from app.modules.assignments.service import AssignmentService
from app.modules.auth.dependencies import CurrentTeacher, CurrentUser
from app.modules.exam_sessions.schemas import SessionStartResponse
from app.modules.start_deutsch.schemas import StartDeutschSessionResponse
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


def _download(filename: str, content: bytes, media_type: str) -> Response:
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Enseignant : banque et création (routes fixes avant /{assignment_id}) ──

@router.get("/bank", response_model=list[BankSubjectResponse])
async def subject_bank(
    teacher: CurrentTeacher,
    level_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Banque de sujets privés disponibles pour les devoirs."""
    return await AssignmentService(db).bank(teacher, level_id)


@router.post("", response_model=AssignmentDetailResponse, status_code=201)
async def create_assignment(
    data: AssignmentCreate, teacher: CurrentTeacher, db: AsyncSession = Depends(get_db)
):
    return await AssignmentService(db).create(teacher, data)


@router.get("/teaching", response_model=list[AssignmentSummaryResponse])
async def my_teaching_assignments(teacher: CurrentTeacher, db: AsyncSession = Depends(get_db)):
    return await AssignmentService(db).list_for_teacher(teacher)


# ── Élève ────────────────────────────────────────────────

@router.get("/me", response_model=list[StudentAssignmentResponse])
async def my_assignments(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    """Devoirs de l'élève : statut et note finale uniquement."""
    return await AssignmentService(db).list_for_student(current_user)


@router.post("/{assignment_id}/start", response_model=SessionStartResponse)
async def start_assignment(
    assignment_id: UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    """Démarre (ou reprend) le devoir : renvoie le contenu du sujet pour le lecteur d'examen."""
    return await AssignmentService(db).start(current_user, assignment_id)


@router.post("/{assignment_id}/start-deutsch/start", response_model=StartDeutschSessionResponse)
async def start_start_deutsch_assignment(
    assignment_id: UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    """Devoir Start Deutsch : démarre (ou reprend) la session du lecteur A1/A2."""
    return await AssignmentService(db).start_start_deutsch(current_user, assignment_id)


# ── Enseignant : suivi et correction ─────────────────────

@router.get("/{assignment_id}", response_model=AssignmentDetailResponse)
async def assignment_detail(
    assignment_id: UUID, teacher: CurrentTeacher, db: AsyncSession = Depends(get_db)
):
    return await AssignmentService(db).get_detail(teacher, assignment_id)


@router.post("/{assignment_id}/cancel", response_model=SuccessResponse)
async def cancel_assignment(
    assignment_id: UUID, teacher: CurrentTeacher, db: AsyncSession = Depends(get_db)
):
    await AssignmentService(db).cancel(teacher, assignment_id)
    return SuccessResponse(message="Devoir annulé.")


@router.get("/{assignment_id}/schreiben.zip")
async def download_all_schreiben(
    assignment_id: UUID, teacher: CurrentTeacher, db: AsyncSession = Depends(get_db)
):
    filename, content = await AssignmentService(db).schreiben_zip(teacher, assignment_id)
    return _download(filename, content, "application/zip")


@router.get("/{assignment_id}/submissions/{student_id}", response_model=SubmissionGradingResponse)
async def submission_for_grading(
    assignment_id: UUID, student_id: UUID, teacher: CurrentTeacher, db: AsyncSession = Depends(get_db)
):
    return await AssignmentService(db).get_submission_for_grading(teacher, assignment_id, student_id)


@router.post("/{assignment_id}/submissions/{student_id}/grade", response_model=SubmissionGradingResponse)
async def grade_submission(
    assignment_id: UUID,
    student_id: UUID,
    data: GradeRequest,
    teacher: CurrentTeacher,
    db: AsyncSession = Depends(get_db),
):
    return await AssignmentService(db).grade(teacher, assignment_id, student_id, data)


@router.get("/{assignment_id}/submissions/{student_id}/schreiben.pdf")
async def download_schreiben(
    assignment_id: UUID, student_id: UUID, teacher: CurrentTeacher, db: AsyncSession = Depends(get_db)
):
    filename, content = await AssignmentService(db).schreiben_pdf(teacher, assignment_id, student_id)
    return _download(filename, content, "application/pdf")


@router.post("/{assignment_id}/submissions/{student_id}/annotated", response_model=SuccessResponse)
async def upload_annotated_copy(
    assignment_id: UUID,
    student_id: UUID,
    teacher: CurrentTeacher,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    await AssignmentService(db).upload_annotated(teacher, assignment_id, student_id, file)
    return SuccessResponse(message="Copie annotée enregistrée.")


@router.get("/{assignment_id}/submissions/{student_id}/annotated")
async def download_annotated_copy(
    assignment_id: UUID, student_id: UUID, teacher: CurrentTeacher, db: AsyncSession = Depends(get_db)
):
    path = await AssignmentService(db).annotated_path(teacher, assignment_id, student_id)
    return FileResponse(path, filename=path.name)