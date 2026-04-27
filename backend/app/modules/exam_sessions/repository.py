"""
app/modules/exam_sessions/repository.py
"""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.modules.exam_sessions.models import ExamSession, ExamSessionAnswer
from app.shared.database.repository import BaseRepository


class ExamSessionRepository(BaseRepository[ExamSession]):

    def __init__(self, db: AsyncSession):
        super().__init__(ExamSession, db)

    async def get_active_session(
        self, user_id: UUID, exam_id: UUID
    ) -> ExamSession | None:
        """Retourne la session IN_PROGRESS si elle existe."""
        result = await self.db.execute(
            select(ExamSession)
            .where(
                ExamSession.user_id == user_id,
                ExamSession.exam_id == exam_id,
                ExamSession.status == "IN_PROGRESS",
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[ExamSession]:
        result = await self.db.execute(
            select(ExamSession)
            .where(ExamSession.user_id == user_id)
            .order_by(ExamSession.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_answers(self, session_id: UUID) -> ExamSession | None:
        result = await self.db.execute(
            select(ExamSession)
            .options(selectinload(ExamSession.answers))
            .where(ExamSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_done_subject_ids(
        self, user_id: UUID, exam_id: UUID
    ) -> list[UUID]:
        """
        Retourne les subject_id déjà complétés (COMPLETED ou PENDING_REVIEW)
        par ce user sur cet exam. Utilisé pour choisir le prochain sujet.
        """
        result = await self.db.execute(
            select(ExamSession.subject_id)
            .where(
                ExamSession.user_id == user_id,
                ExamSession.exam_id == exam_id,
                ExamSession.status.in_(["COMPLETED", "PENDING_REVIEW"]),
            )
        )
        return list(result.scalars().all())


class ExamSessionAnswerRepository(BaseRepository[ExamSessionAnswer]):

    def __init__(self, db: AsyncSession):
        super().__init__(ExamSessionAnswer, db)

    async def find_by_session_and_question(
        self, session_id: UUID, question_id: UUID
    ) -> ExamSessionAnswer | None:
        result = await self.db.execute(
            select(ExamSessionAnswer)
            .where(
                ExamSessionAnswer.session_id == session_id,
                ExamSessionAnswer.question_id == question_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_session(
        self, session_id: UUID
    ) -> list[ExamSessionAnswer]:
        result = await self.db.execute(
            select(ExamSessionAnswer)
            .where(ExamSessionAnswer.session_id == session_id)
        )
        return list(result.scalars().all())

    async def upsert(
        self,
        session_id: UUID,
        question_id: UUID,
        user_answer: dict,
    ) -> ExamSessionAnswer:
        existing = await self.find_by_session_and_question(session_id, question_id)
        if existing:
            return await self.update(existing.id, user_answer=user_answer)
        return await self.create(
            session_id=session_id,
            question_id=question_id,
            user_answer=user_answer,
        )