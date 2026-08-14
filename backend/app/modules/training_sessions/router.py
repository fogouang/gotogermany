"""
app/modules/training_sessions/router.py
"""
from uuid import UUID
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentDirector, CurrentSecretary, CurrentCenterStaff, CurrentTeacher
from app.modules.training_sessions.schemas import (
    TrainingSessionCreateRequest,
    TrainingSessionUpdateRequest,
    TrainingSessionResponse,
    TeacherAssignRequest,
    StudentEnrollRequest,
    StudentEndRequest,
    TrainingSessionStatsResponse,
    TeacherCommentCreateRequest,
    TeacherCommentResponse,
)
from app.modules.training_sessions.service import TrainingSessionService, _to_response
from app.modules.training_sessions.repository import TrainingSessionRepository
from app.modules.users.schemas import StudentDetailedProgressResponse, StudentProgressResponse
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


@router.post("", response_model=TrainingSessionResponse, status_code=201)
async def create_session(
    data: TrainingSessionCreateRequest,
    staff: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    session = await TrainingSessionService(db).create_session(data, staff)
    full = await TrainingSessionRepository(db).get_with_relations_or_404(session.id)
    return _to_response(full)


@router.get("/by-center", response_model=list[TrainingSessionResponse])
async def list_sessions_by_center(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await TrainingSessionService(db).list_for_director(current_director)


@router.get("/by-branch", response_model=list[TrainingSessionResponse])
async def list_sessions_by_branch(
    current_secretary: CurrentSecretary,
    db: AsyncSession = Depends(get_db),
):
    return await TrainingSessionService(db).list_for_secretary(current_secretary)


@router.get("/mine", response_model=list[TrainingSessionResponse])
async def list_my_sessions(
    current_teacher: CurrentTeacher,
    db: AsyncSession = Depends(get_db),
):
    return await TrainingSessionService(db).list_for_teacher(current_teacher)

@router.get("/students/progress", response_model=list[StudentProgressResponse])
async def get_students_progress_for_teacher(
    current_teacher: CurrentTeacher,
    db: AsyncSession = Depends(get_db),
):
    """Progression agrégée (score moyen, dernière session...) des
    étudiants actifs de l'enseignant, dédupliquée à travers ses sessions."""
    from app.modules.users.service import UserService

    return await UserService(db).get_student_progress_for_teacher(current_teacher)


@router.patch("/{session_id}", response_model=TrainingSessionResponse)
async def update_session(
    session_id: UUID,
    data: TrainingSessionUpdateRequest,
    staff: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    await TrainingSessionService(db).update_session(session_id, data, staff)
    full = await TrainingSessionRepository(db).get_with_relations_or_404(session_id)
    return _to_response(full)


@router.post("/{session_id}/teachers", response_model=SuccessResponse)
async def assign_teacher(
    session_id: UUID,
    data: TeacherAssignRequest,
    staff: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    await TrainingSessionService(db).assign_teacher(session_id, data.teacher_id, staff)
    return SuccessResponse(message="Enseignant assigné à la session.")


@router.delete("/{session_id}/teachers/{teacher_id}", response_model=SuccessResponse)
async def remove_teacher(
    session_id: UUID,
    teacher_id: UUID,
    staff: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    await TrainingSessionService(db).remove_teacher(session_id, teacher_id, staff)
    return SuccessResponse(message="Enseignant retiré de la session.")


@router.post("/{session_id}/students", response_model=SuccessResponse)
async def enroll_student(
    session_id: UUID,
    data: StudentEnrollRequest,
    staff: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    await TrainingSessionService(db).enroll_student(session_id, data.student_id, staff)
    return SuccessResponse(message="Étudiant inscrit à la session.")


@router.patch("/{session_id}/students/{student_id}/end", response_model=SuccessResponse)
async def end_student(
    session_id: UUID,
    student_id: UUID,
    data: StudentEndRequest,
    staff: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    await TrainingSessionService(db).end_student(session_id, student_id, data.ended_at, staff)
    return SuccessResponse(message="Étudiant marqué comme terminé.")


@router.get("/{session_id}/stats", response_model=TrainingSessionStatsResponse)
async def get_session_stats(
    session_id: UUID,
    staff: CurrentCenterStaff,
    db: AsyncSession = Depends(get_db),
):
    return await TrainingSessionService(db).get_stats(session_id, staff)


# ── Vue enseignant sur un étudiant ────────────────────────

@router.get("/students/{student_id}/progress", response_model=StudentDetailedProgressResponse)
async def get_student_progress_for_teacher(
    student_id: UUID,
    current_teacher: CurrentTeacher,
    db: AsyncSession = Depends(get_db),
):
    from app.modules.users.service import UserService
    return await UserService(db).get_student_progress_detail_for_teacher(student_id, current_teacher)


@router.get("/students/{student_id}/sessions/{session_id}/result")
async def get_student_session_result_for_teacher(
    student_id: UUID,
    session_id: UUID,
    current_teacher: CurrentTeacher,
    db: AsyncSession = Depends(get_db),
):
    from app.modules.exam_sessions.service import ExamSessionService

    await TrainingSessionService(db).assert_teacher_can_view_student(current_teacher, student_id)
    return await ExamSessionService(db).get_result_for_staff(session_id, student_id)


@router.post("/students/{student_id}/comments", response_model=TeacherCommentResponse, status_code=201)
async def add_student_comment(
    student_id: UUID,
    data: TeacherCommentCreateRequest,
    current_teacher: CurrentTeacher,
    db: AsyncSession = Depends(get_db),
):
    c = await TrainingSessionService(db).add_comment(student_id, data.comment, current_teacher)
    return TeacherCommentResponse(
        id=c.id, teacher_id=c.teacher_id, teacher_name=current_teacher.full_name,
        comment=c.comment, created_at=c.created_at,
    )


@router.get("/students/{student_id}/comments", response_model=list[TeacherCommentResponse])
async def list_student_comments_for_teacher(
    student_id: UUID,
    current_teacher: CurrentTeacher,
    db: AsyncSession = Depends(get_db),
):
    return await TrainingSessionService(db).list_comments_for_teacher(student_id, current_teacher)


@router.get("/students/{student_id}/comments/all", response_model=list[TeacherCommentResponse])
async def list_student_comments_for_director(
    student_id: UUID,
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    return await TrainingSessionService(db).list_comments_for_director(student_id, current_director)