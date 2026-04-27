"""
app/modules/exam_sessions/router.py
"""
from uuid import UUID
import uuid

from fastapi import Depends, File, HTTPException, Path, UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentUser
from app.modules.exam_sessions.schemas import (
    ActiveSessionResponse,
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    BulkAnswerSubmitRequest,
    SessionListResponse,
    SessionResultResponse,
    SessionStartRequest,
    SessionStartResponse,
)
from app.modules.exam_sessions.service import ExamSessionService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


@router.post("", response_model=SessionStartResponse, status_code=201)
async def start_session(
    data: SessionStartRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Démarre une session d'examen.
    Retourne tout le contenu de l'exam (modules + teile + questions).
    """
    return await ExamSessionService(db).start_session(
        user_id=current_user.id,
        exam_id=data.exam_id,
        subject_id=data.subject_id,
    )


@router.get("", response_model=list[SessionListResponse])
async def get_my_sessions(
    skip: int = 0,
    limit: int = 20,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Liste toutes les sessions de l'utilisateur connecté."""
    return await ExamSessionService(db).get_my_sessions(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

@router.get("/active", response_model=ActiveSessionResponse | None)
async def get_active_session(
    exam_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Retourne la session IN_PROGRESS pour un exam donné.
    Retourne null si aucune session active.
    """
    from app.modules.exam_sessions.repository import ExamSessionRepository
    from app.modules.exam_sessions.repository import ExamSessionAnswerRepository
    from app.modules.exams.repository import ExamRepository
    from app.modules.exams.repository import SubjectRepository

    repo = ExamSessionRepository(db)
    answer_repo = ExamSessionAnswerRepository(db)
    exam_repo = ExamRepository(db)

    session = await repo.get_active_by_exam(current_user.id, exam_id)
    if not session:
        return None

    exam = await exam_repo.get_by_id(exam_id)
    subject = await SubjectRepository(db).get_by_id(session.subject_id)
    answers = await answer_repo.get_by_session(session.id)

    return ActiveSessionResponse(
        session_id=session.id,
        exam_id=session.exam_id,
        exam_name=exam.name if exam else "",
        subject_id=session.subject_id,
        subject_number=subject.subject_number if subject else 0,
        status=session.status,
        started_at=session.started_at,
        answered_questions=len(answers),
        total_questions=0,  # calculé côté frontend depuis le store
    )
    
    
@router.post("/{session_id}/answers", response_model=AnswerSubmitResponse)
async def submit_answer(
    session_id: UUID,
    data: AnswerSubmitRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Soumet une réponse à une question.
    Peut être appelé plusieurs fois — upsert à chaque appel.
    Pour les questions auto-correctable, retourne is_correct immédiatement.
    """
    return await ExamSessionService(db).submit_answer(
        session_id=session_id,
        user_id=current_user.id,
        data=data,
    )


@router.post("/{session_id}/answers/bulk", response_model=list[AnswerSubmitResponse])
async def submit_bulk_answers(
    session_id: UUID,
    data: BulkAnswerSubmitRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Soumission groupée — pour sauvegarder un Teil entier en une fois.
    Utile avant timeout ou changement de module.
    """
    return await ExamSessionService(db).submit_bulk_answers(
        session_id=session_id,
        user_id=current_user.id,
        data=data,
    )


@router.post("/{session_id}/submit", response_model=SessionResultResponse)
async def submit_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Soumet la session complète.
    Calcule le score final et retourne le résultat détaillé.
    Status → COMPLETED ou PENDING_REVIEW si Schreiben/Sprechen présents.
    """
    return await ExamSessionService(db).submit_session(
        session_id=session_id,
        user_id=current_user.id,
    )


@router.get("/{session_id}/result", response_model=SessionResultResponse)
async def get_result(
    session_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Consulte le résultat d'une session soumise.
    Révèle les correct_answer pour chaque question.
    """
    return await ExamSessionService(db).get_result(
        session_id=session_id,
        user_id=current_user.id,
    )
    
    
# @router.post("/{session_id}/upload-audio")
async def upload_session_audio(
    session_id: uuid.UUID,
    teil_number: int,
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Upload audio Sprechen pour une session.
    Retourne le chemin relatif à stocker dans user_answer.
    
    À ajouter dans router.py :
    
    @router.post("/{session_id}/upload-audio")
    async def upload_session_audio(...):
    """
    # Vérifier que la session appartient au user
    from app.modules.exam_sessions.repository import ExamSessionRepository
    repo = ExamSessionRepository(db)
    session = await repo.get_by_id(session_id)
 
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable.")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé.")
    if session.status != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="Session non active.")
 
    # Vérifier le type de fichier
    allowed = {"audio/webm", "audio/ogg", "audio/mp4", "audio/wav"}
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non supporté : {file.content_type}"
        )
 
    # Créer le dossier session
    session_dir = Path("storage/audio/sessions") / str(session_id)
    session_dir.mkdir(parents=True, exist_ok=True)
 
    # Nom du fichier
    ext = file.filename.split(".")[-1] if file.filename else "webm"
    filename = f"sprechen_teil{teil_number}.{ext}"
    file_path = session_dir / filename
 
    # Sauvegarder
    content = await file.read()
    file_path.write_bytes(content)
 
    # Chemin relatif pour la BD
    relative_path = f"sessions/{session_id}/{filename}"
 
    return {"audio_file": relative_path, "url": f"/audio/{relative_path}"}