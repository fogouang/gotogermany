"""
app/modules/training_sessions/service.py
"""
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.training_sessions.models import (
    TrainingSession,
    TrainingSessionTeacher,
    TrainingSessionStudent,
    TeacherStudentComment,
)
from app.modules.training_sessions.repository import (
    TrainingSessionRepository,
    TrainingSessionTeacherRepository,
    TrainingSessionStudentRepository,
    TeacherStudentCommentRepository,
)
from app.modules.training_sessions.schemas import (
    TrainingSessionCreateRequest,
    TrainingSessionUpdateRequest,
    TrainingSessionResponse,
    TrainingSessionTeacherResponse,
    TrainingSessionStudentResponse,
    TrainingSessionStatsResponse,
    TeacherCommentResponse,
)
from app.modules.users.models import User, UserRole
from app.shared.exceptions.http import BadRequestException, ForbiddenException, NotFoundException


class TrainingSessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = TrainingSessionRepository(db)
        self.teacher_link_repo = TrainingSessionTeacherRepository(db)
        self.student_link_repo = TrainingSessionStudentRepository(db)
        self.comment_repo = TeacherStudentCommentRepository(db)

    # ── Création / staff ──────────────────────

    async def create_session(
        self, data: TrainingSessionCreateRequest, staff: User
    ) -> TrainingSession:
        from app.modules.centers.repository import BranchRepository
        from app.modules.exams.repository import LevelRepository

        branch_repo = BranchRepository(self.db)

        if staff.role == UserRole.center_director:
            if not data.branch_id:
                raise BadRequestException(detail="branch_id requis pour un directeur.")
            branch = await branch_repo.get_by_id_or_404(data.branch_id)
            if branch.center_id != staff.center_id:
                raise ForbiddenException(detail="Cette succursale n'appartient pas à votre centre.")
        elif staff.role == UserRole.branch_secretary:
            branch = await branch_repo.get_by_id_or_404(staff.branch_id)
        else:
            raise ForbiddenException(detail="Action réservée au staff de centre.")

        # Niveau du catalogue des examens (B1/B2), ou niveau Start Deutsch (A1/A2)
        if data.level_id:
            await LevelRepository(self.db).get_by_id_or_404(data.level_id)

        # On valide tout le monde AVANT de créer la classe : pas de classe à moitié créée
        teacher_ids = list(dict.fromkeys(data.teacher_ids))
        student_ids = list(dict.fromkeys(data.student_ids))
        for teacher_id in teacher_ids:
            await self._validate_teacher(branch.center_id, teacher_id)
        for student_id in student_ids:
            await self._validate_student(branch.id, student_id)

        session = await self.session_repo.create(
            branch_id=branch.id,
            level_id=data.level_id,
            sd_level=data.sd_level,
            label=data.label,
            start_date=data.start_date,
            end_date=data.end_date,
            created_by=staff.id,
        )

        now = datetime.now(timezone.utc)
        for teacher_id in teacher_ids:
            await self.teacher_link_repo.create(training_session_id=session.id, teacher_id=teacher_id)
        for student_id in student_ids:
            await self.student_link_repo.create(
                training_session_id=session.id, student_id=student_id, enrolled_at=now
            )
            await self._sync_student_level(student_id, session)
        return session

    async def update_session(
        self, session_id: UUID, data: TrainingSessionUpdateRequest, staff: User
    ) -> TrainingSession:
        session = await self._get_session_scoped(session_id, staff)
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return session
        return await self.session_repo.update(session_id, **update_data)

    async def assign_teacher(self, session_id: UUID, teacher_id: UUID, staff: User) -> None:
        from app.modules.centers.repository import BranchRepository

        session = await self._get_session_scoped(session_id, staff)
        branch = await BranchRepository(self.db).get_by_id_or_404(session.branch_id)
        await self._validate_teacher(branch.center_id, teacher_id)

        if await self.teacher_link_repo.find_link(session_id, teacher_id):
            return
        await self.teacher_link_repo.create(training_session_id=session_id, teacher_id=teacher_id)

    async def enroll_student(self, session_id: UUID, student_id: UUID, staff: User) -> None:
        session = await self._get_session_scoped(session_id, staff)
        await self._validate_student(session.branch_id, student_id)

        if await self.student_link_repo.find_link(session_id, student_id):
            return
        await self.student_link_repo.create(
            training_session_id=session_id,
            student_id=student_id,
            enrolled_at=datetime.now(timezone.utc),
        )
        await self._sync_student_level(student_id, session)

    async def _sync_student_level(self, student_id: UUID, session: TrainingSession) -> None:
        """Le parcours de l'élève suit sa classe.
        Classe A1/A2 : parcours start_deutsch et niveau de la classe.
        Classe B pour un élève qui était en Start Deutsch : retour au parcours exam.
        Un élève déjà en parcours exam n'est pas touché (comportement d'avant)."""
        from app.modules.users.repository import UserRepository

        user_repo = UserRepository(self.db)
        student = await user_repo.get_by_id_or_404(student_id)
        if session.sd_level:
            await user_repo.update(
                student.id,
                learning_track="start_deutsch",
                target_sd_level=session.sd_level,
                target_level_id=None,
            )
        elif student.learning_track == "start_deutsch" or student.target_sd_level:
            await user_repo.update(
                student.id,
                learning_track="exam",
                target_sd_level=None,
                target_level_id=session.level_id,
            )

    async def _validate_teacher(self, center_id: UUID, teacher_id: UUID) -> User:
        """L'enseignant doit exister et appartenir au même centre que la classe."""
        from app.modules.centers.repository import BranchRepository
        from app.modules.users.repository import UserRepository

        teacher = await UserRepository(self.db).get_by_id_or_404(teacher_id)
        if teacher.role != UserRole.teacher:
            raise BadRequestException(detail="Cet utilisateur n'est pas un enseignant.")
        if not teacher.branch_id:
            raise ForbiddenException(detail="Cet enseignant n'appartient pas à votre centre.")
        teacher_branch = await BranchRepository(self.db).get_by_id_or_404(teacher.branch_id)
        if teacher_branch.center_id != center_id:
            raise ForbiddenException(detail="Cet enseignant n'appartient pas à votre centre.")
        return teacher

    async def _validate_student(self, branch_id: UUID, student_id: UUID) -> User:
        """L'élève doit exister et appartenir à la succursale de la classe."""
        from app.modules.users.repository import UserRepository

        student = await UserRepository(self.db).get_by_id_or_404(student_id)
        if student.role != UserRole.student:
            raise BadRequestException(detail="Cet utilisateur n'est pas un étudiant.")
        if student.branch_id != branch_id:
            raise BadRequestException(
                detail="Cet étudiant n'appartient pas à la succursale de la classe."
            )
        return student
    

    async def remove_teacher(self, session_id: UUID, teacher_id: UUID, staff: User) -> None:
        await self._get_session_scoped(session_id, staff)
        link = await self.teacher_link_repo.find_link(session_id, teacher_id)
        if link:
            await self.teacher_link_repo.delete(link.id)


    async def end_student(
        self, session_id: UUID, student_id: UUID, ended_at: datetime | None, staff: User
    ) -> None:
        await self._get_session_scoped(session_id, staff)
        link = await self.student_link_repo.find_link(session_id, student_id)
        if not link:
            raise NotFoundException(detail="Cet étudiant n'est pas inscrit à cette session.")
        await self.student_link_repo.update(
            link.id, ended_at=ended_at or datetime.now(timezone.utc)
        )

    async def _get_session_scoped(self, session_id: UUID, staff: User) -> TrainingSession:
        from app.modules.centers.repository import BranchRepository

        session = await self.session_repo.get_by_id_or_404(session_id)
        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(session.branch_id)

        if staff.role == UserRole.center_director:
            if branch.center_id != staff.center_id:
                raise ForbiddenException(detail="Cette session n'appartient pas à votre centre.")
        elif staff.role == UserRole.branch_secretary:
            if session.branch_id != staff.branch_id:
                raise ForbiddenException(detail="Cette session n'appartient pas à votre succursale.")
        else:
            raise ForbiddenException(detail="Action réservée au staff de centre.")
        return session

    # ── Listing ────────────────────────────────

    async def list_for_director(self, director: User) -> list[TrainingSessionResponse]:
        sessions = await self.session_repo.find_by_center(director.center_id)
        return [_to_response(s) for s in sessions]

    async def list_for_secretary(self, secretary: User) -> list[TrainingSessionResponse]:
        sessions = await self.session_repo.find_by_branch(secretary.branch_id)
        return [_to_response(s) for s in sessions]

    async def list_for_teacher(self, teacher: User) -> list[TrainingSessionResponse]:
        sessions = await self.teacher_link_repo.find_sessions_for_teacher(teacher.id)
        return [_to_response(s) for s in sessions if not _is_draft(s)]

    async def get_stats(self, session_id: UUID, staff: User) -> TrainingSessionStatsResponse:
        await self._get_session_scoped(session_id, staff)
        started = await self.student_link_repo.count_started(session_id)
        ended = await self.student_link_repo.count_ended(session_id)
        return TrainingSessionStatsResponse(
            total_started=started, total_ended=ended, total_active=started - ended
        )

    # ── Autorisation live_session / vue progression ──────

    async def assert_can_launch_live_session(self, actor: User, student_id: UUID) -> None:
        """Directeur : accès à tout son centre. Secrétaire : sa succursale
        (droit déjà existant, conservé). Enseignant : uniquement s'il
        partage une session active avec cet étudiant."""
        from app.modules.users.repository import UserRepository
        from app.modules.centers.repository import BranchRepository

        student = await UserRepository(self.db).get_by_id_or_404(student_id)
        if student.role != UserRole.student:
            raise BadRequestException(detail="Cet utilisateur n'est pas un étudiant.")

        branch_repo = BranchRepository(self.db)

        if actor.role == UserRole.center_director:
            if student.branch_id is None:
                raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre centre.")
            branch = await branch_repo.get_by_id_or_404(student.branch_id)
            if branch.center_id != actor.center_id:
                raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre centre.")
            return

        if actor.role == UserRole.branch_secretary:
            if student.branch_id != actor.branch_id:
                raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre succursale.")
            return

        if actor.role == UserRole.teacher:
            allowed = await self.teacher_link_repo.teacher_shares_session_with_student(
                actor.id, student_id
            )
            if not allowed:
                raise ForbiddenException(
                    detail="Vous n'êtes pas assigné à une session active avec cet étudiant."
                )
            return

        raise ForbiddenException(detail="Action réservée au staff de centre ou aux enseignants.")

    async def assert_teacher_can_view_student(self, teacher: User, student_id: UUID) -> None:
        if teacher.role != UserRole.teacher:
            raise ForbiddenException(detail="Action réservée aux enseignants.")
        allowed = await self.teacher_link_repo.teacher_shares_session_with_student(
            teacher.id, student_id
        )
        if not allowed:
            raise ForbiddenException(
                detail="Vous n'êtes pas assigné à une session active avec cet étudiant."
            )

    # ── Commentaires enseignant ───────────────────────────

    async def add_comment(self, student_id: UUID, comment: str, teacher: User) -> TeacherStudentComment:
        await self.assert_teacher_can_view_student(teacher, student_id)
        return await self.comment_repo.create(
            teacher_id=teacher.id, student_id=student_id, comment=comment
        )

    async def list_comments_for_teacher(
        self, student_id: UUID, teacher: User
    ) -> list[TeacherCommentResponse]:
        await self.assert_teacher_can_view_student(teacher, student_id)

        result = await self.db.execute(
            select(TrainingSessionTeacher.teacher_id)
            .join(
                TrainingSessionStudent,
                TrainingSessionStudent.training_session_id == TrainingSessionTeacher.training_session_id,
            )
            .where(
                TrainingSessionStudent.student_id == student_id,
                TrainingSessionStudent.ended_at.is_(None),
            )
        )
        visible_teacher_ids = {row[0] for row in result.all()}
        visible_teacher_ids.add(teacher.id)

        comments = await self.comment_repo.find_visible_for_student(student_id, visible_teacher_ids)
        return [
            TeacherCommentResponse(
                id=c.id, teacher_id=c.teacher_id, teacher_name=c.teacher.full_name,
                comment=c.comment, created_at=c.created_at,
            )
            for c in comments
        ]

    async def list_comments_for_director(
        self, student_id: UUID, director: User
    ) -> list[TeacherCommentResponse]:
        from app.modules.centers.repository import BranchRepository
        from app.modules.users.repository import UserRepository

        student = await UserRepository(self.db).get_by_id_or_404(student_id)
        branch = await BranchRepository(self.db).get_by_id_or_404(student.branch_id)
        if branch.center_id != director.center_id:
            raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre centre.")

        comments = await self.comment_repo.find_all_for_student(student_id)
        return [
            TeacherCommentResponse(
                id=c.id, teacher_id=c.teacher_id, teacher_name=c.teacher.full_name,
                comment=c.comment, created_at=c.created_at,
            )
            for c in comments
        ]


def _is_draft(session: TrainingSession) -> bool:
    """Brouillon : aucun élève actif (jamais inscrit, ou tous terminés)."""
    return not any(link.ended_at is None for link in session.student_links)


def _cefr_code(session: TrainingSession) -> str:
    """B1, B2... pour une classe d'examen, A1 ou A2 pour Start Deutsch."""
    if session.sd_level:
        return session.sd_level
    return session.level.cefr_code if session.level else ""


def _level_label(session: TrainingSession) -> str:
    if session.sd_level:
        return f"Start Deutsch {session.sd_level}"
    level = session.level
    if not level:
        return ""
    exam = getattr(level, "exam", None)
    return exam.name if exam else level.cefr_code


def _to_response(session: TrainingSession) -> TrainingSessionResponse:
    return TrainingSessionResponse(
        id=session.id,
        branch_id=session.branch_id,
        branch_name=session.branch.name if session.branch else "",
        track=session.track,
        level_id=session.level_id,
        sd_level=session.sd_level,
        cefr_code=_cefr_code(session),
        level_name=_level_label(session),
        label=session.label,
        start_date=session.start_date,
        end_date=session.end_date,
        created_at=session.created_at,
        is_draft=_is_draft(session),
        teachers=[
            TrainingSessionTeacherResponse(teacher_id=t.teacher_id, teacher_name=t.teacher.full_name)
            for t in session.teacher_links
        ],
        students=[
            TrainingSessionStudentResponse(
                student_id=s.student_id,
                student_name=s.student.full_name,
                enrolled_at=s.enrolled_at,
                ended_at=s.ended_at,
            )
            for s in session.student_links
        ],
    )