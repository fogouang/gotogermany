"""
app/modules/training_sessions/repository.py
"""
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.training_sessions.models import (
    TrainingSession,
    TrainingSessionTeacher,
    TrainingSessionStudent,
    TeacherStudentComment,
)
from app.modules.centers.models import Branch
from app.shared.database.repository import BaseRepository


class TrainingSessionRepository(BaseRepository[TrainingSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingSession, db)

    async def get_with_relations_or_404(self, session_id: UUID) -> TrainingSession:
        result = await self.db.execute(
            select(TrainingSession)
            .options(
                selectinload(TrainingSession.branch),
                selectinload(TrainingSession.level),
                selectinload(TrainingSession.teacher_links).selectinload(TrainingSessionTeacher.teacher),
                selectinload(TrainingSession.student_links).selectinload(TrainingSessionStudent.student),
            )
            .where(TrainingSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            from app.shared.exceptions.http import NotFoundException
            raise NotFoundException(detail="Session introuvable.")
        return session

    async def find_by_branch(self, branch_id: UUID) -> list[TrainingSession]:
        result = await self.db.execute(
            select(TrainingSession)
            .options(
                selectinload(TrainingSession.level),
                selectinload(TrainingSession.teacher_links).selectinload(TrainingSessionTeacher.teacher),
                selectinload(TrainingSession.student_links).selectinload(TrainingSessionStudent.student),
            )
            .where(TrainingSession.branch_id == branch_id)
            .order_by(TrainingSession.start_date.desc())
        )
        return list(result.scalars().all())

    async def find_by_center(self, center_id: UUID) -> list[TrainingSession]:
        result = await self.db.execute(
            select(TrainingSession)
            .join(Branch, Branch.id == TrainingSession.branch_id)
            .options(
                selectinload(TrainingSession.branch),
                selectinload(TrainingSession.level),
                selectinload(TrainingSession.teacher_links).selectinload(TrainingSessionTeacher.teacher),
                selectinload(TrainingSession.student_links).selectinload(TrainingSessionStudent.student),
            )
            .where(Branch.center_id == center_id)
            .order_by(TrainingSession.start_date.desc())
        )
        return list(result.scalars().all())


class TrainingSessionTeacherRepository(BaseRepository[TrainingSessionTeacher]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingSessionTeacher, db)

    async def find_link(self, session_id: UUID, teacher_id: UUID) -> TrainingSessionTeacher | None:
        result = await self.db.execute(
            select(TrainingSessionTeacher).where(
                TrainingSessionTeacher.training_session_id == session_id,
                TrainingSessionTeacher.teacher_id == teacher_id,
            )
        )
        return result.scalar_one_or_none()

    async def find_sessions_for_teacher(self, teacher_id: UUID) -> list[TrainingSession]:
        """Retourne directement les TrainingSession (pas les liens), avec
        toutes les relations nécessaires en un seul select — évite le bug
        d'identity map d'un second select sur le même objet déjà en mémoire."""
        result = await self.db.execute(
            select(TrainingSession)
            .join(
                TrainingSessionTeacher,
                TrainingSessionTeacher.training_session_id == TrainingSession.id,
            )
            .options(
                selectinload(TrainingSession.branch),
                selectinload(TrainingSession.level),
                selectinload(TrainingSession.teacher_links).selectinload(TrainingSessionTeacher.teacher),
                selectinload(TrainingSession.student_links).selectinload(TrainingSessionStudent.student),
            )
            .where(TrainingSessionTeacher.teacher_id == teacher_id)
        )
        return list(result.scalars().all())

    async def teacher_shares_session_with_student(self, teacher_id: UUID, student_id: UUID) -> bool:
        """Coeur du check de permission live_session/vue progression : l'enseignant
        est-il assigné à une session où l'étudiant est inscrit et encore actif ?"""
        result = await self.db.execute(
            select(func.count(TrainingSessionTeacher.id))
            .join(
                TrainingSessionStudent,
                TrainingSessionStudent.training_session_id == TrainingSessionTeacher.training_session_id,
            )
            .where(
                TrainingSessionTeacher.teacher_id == teacher_id,
                TrainingSessionStudent.student_id == student_id,
                TrainingSessionStudent.ended_at.is_(None),
            )
        )
        return result.scalar_one() > 0

    async def find_active_student_ids_for_teacher(self, teacher_id: UUID) -> list[UUID]:
        result = await self.db.execute(
            select(TrainingSessionStudent.student_id)
            .distinct()
            .join(
                TrainingSessionTeacher,
                TrainingSessionTeacher.training_session_id == TrainingSessionStudent.training_session_id,
            )
            .where(
                TrainingSessionTeacher.teacher_id == teacher_id,
                TrainingSessionStudent.ended_at.is_(None),
            )
        )
        return [row[0] for row in result.all()]
    

class TrainingSessionStudentRepository(BaseRepository[TrainingSessionStudent]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingSessionStudent, db)

    async def find_link(self, session_id: UUID, student_id: UUID) -> TrainingSessionStudent | None:
        result = await self.db.execute(
            select(TrainingSessionStudent).where(
                TrainingSessionStudent.training_session_id == session_id,
                TrainingSessionStudent.student_id == student_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_started(self, session_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(TrainingSessionStudent.id)).where(
                TrainingSessionStudent.training_session_id == session_id
            )
        )
        return result.scalar_one()

    async def count_ended(self, session_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(TrainingSessionStudent.id)).where(
                TrainingSessionStudent.training_session_id == session_id,
                TrainingSessionStudent.ended_at.is_not(None),
            )
        )
        return result.scalar_one()


class TeacherStudentCommentRepository(BaseRepository[TeacherStudentComment]):
    def __init__(self, db: AsyncSession):
        super().__init__(TeacherStudentComment, db)

    async def find_visible_for_student(
        self, student_id: UUID, viewer_teacher_ids: set[UUID]
    ) -> list[TeacherStudentComment]:
        result = await self.db.execute(
            select(TeacherStudentComment)
            .options(selectinload(TeacherStudentComment.teacher))
            .where(
                TeacherStudentComment.student_id == student_id,
                TeacherStudentComment.teacher_id.in_(viewer_teacher_ids),
            )
            .order_by(TeacherStudentComment.created_at.desc())
        )
        return list(result.scalars().all())

    async def find_all_for_student(self, student_id: UUID) -> list[TeacherStudentComment]:
        """Vue directeur — tous les commentaires, tous enseignants confondus."""
        result = await self.db.execute(
            select(TeacherStudentComment)
            .options(selectinload(TeacherStudentComment.teacher))
            .where(TeacherStudentComment.student_id == student_id)
            .order_by(TeacherStudentComment.created_at.desc())
        )
        return list(result.scalars().all())