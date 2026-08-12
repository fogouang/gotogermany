"""
app/modules/start_deutsch/repository.py
"""
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.start_deutsch.models import (
    StartDeutschAnswer,
    StartDeutschModule,
    StartDeutschQuestion,
    StartDeutschSchreibenCorrection,
    StartDeutschSession,
    StartDeutschSubject,
    StartDeutschTeil,
)
from app.shared.database.repository import BaseRepository


class SubjectRepository(BaseRepository[StartDeutschSubject]):

    def __init__(self, db: AsyncSession):
        super().__init__(StartDeutschSubject, db)

    async def list_active(self, level: str | None = None) -> list[StartDeutschSubject]:
        stmt = select(StartDeutschSubject).where(StartDeutschSubject.is_active.is_(True))
        if level:
            stmt = stmt.where(StartDeutschSubject.level == level)
        result = await self.db.execute(stmt.order_by(StartDeutschSubject.level, StartDeutschSubject.title))
        return list(result.scalars().all())

    async def list_all(self, level: str | None = None) -> list[StartDeutschSubject]:
        """Vue admin — tous les sujets (actifs ou non), triés par niveau puis numéro."""
        stmt = select(StartDeutschSubject)
        if level:
            stmt = stmt.where(StartDeutschSubject.level == level)
        result = await self.db.execute(
            stmt.order_by(StartDeutschSubject.level, StartDeutschSubject.subject_number)
        )
        return list(result.scalars().all())

    async def get_full_tree(self, subject_id: UUID) -> StartDeutschSubject | None:
        """
        Charge Subject → Module → Teil → Question en une seule requête
        (eager loading explicite — cf. le crash de lazy-load async déjà
        rencontré ailleurs dans le projet sur ce même genre de relation).
        """
        stmt = (
            select(StartDeutschSubject)
            .where(StartDeutschSubject.id == subject_id)
            .options(
                selectinload(StartDeutschSubject.modules)
                .selectinload(StartDeutschModule.teile)
                .selectinload(StartDeutschTeil.questions)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class TeilRepository(BaseRepository[StartDeutschTeil]):

    def __init__(self, db: AsyncSession):
        super().__init__(StartDeutschTeil, db)

    async def get_with_questions(self, teil_id: UUID) -> StartDeutschTeil | None:
        stmt = (
            select(StartDeutschTeil)
            .where(StartDeutschTeil.id == teil_id)
            .options(selectinload(StartDeutschTeil.questions))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_module_and_subject(self, teil_id: UUID) -> StartDeutschTeil | None:
        """
        Charge Teil → Module → Subject + questions en une requête — nécessaire
        pour la correction IA, qui a besoin de connaître le niveau (A1/A2) du
        Subject parent sans déclencher de lazy-load async (lazy="noload" partout).
        """
        stmt = (
            select(StartDeutschTeil)
            .where(StartDeutschTeil.id == teil_id)
            .options(
                selectinload(StartDeutschTeil.questions),
                selectinload(StartDeutschTeil.module).selectinload(StartDeutschModule.subject),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class QuestionRepository(BaseRepository[StartDeutschQuestion]):

    def __init__(self, db: AsyncSession):
        super().__init__(StartDeutschQuestion, db)

    async def get_by_teil(self, teil_id: UUID) -> list[StartDeutschQuestion]:
        result = await self.db.execute(
            select(StartDeutschQuestion)
            .where(StartDeutschQuestion.teil_id == teil_id)
            .order_by(StartDeutschQuestion.question_number)
        )
        return list(result.scalars().all())

    async def get_many_by_ids(self, question_ids: list[UUID]) -> list[StartDeutschQuestion]:
        result = await self.db.execute(
            select(StartDeutschQuestion)
            .where(StartDeutschQuestion.id.in_(question_ids))
            .options(selectinload(StartDeutschQuestion.teil))
        )
        return list(result.scalars().all())

    async def bulk_create(self, questions: list[dict]) -> list[StartDeutschQuestion]:
        """Insert en masse — pour le script d'import de contenu."""
        instances = [StartDeutschQuestion(**q) for q in questions]
        self.db.add_all(instances)
        await self.db.commit()
        for instance in instances:
            await self.db.refresh(instance)
        return instances

    async def delete_by_teil(self, teil_id: UUID) -> int:
        result = await self.db.execute(
            delete(StartDeutschQuestion).where(StartDeutschQuestion.teil_id == teil_id)
        )
        await self.db.commit()
        return result.rowcount


class SessionRepository(BaseRepository[StartDeutschSession]):

    def __init__(self, db: AsyncSession):
        super().__init__(StartDeutschSession, db)

    async def list_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[StartDeutschSession]:
        result = await self.db.execute(
            select(StartDeutschSession)
            .where(StartDeutschSession.user_id == user_id)
            .order_by(StartDeutschSession.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_answers(self, session_id: UUID) -> StartDeutschSession | None:
        stmt = (
            select(StartDeutschSession)
            .where(StartDeutschSession.id == session_id)
            .options(
                selectinload(StartDeutschSession.answers).selectinload(StartDeutschAnswer.question),
                selectinload(StartDeutschSession.schreiben_corrections),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class AnswerRepository(BaseRepository[StartDeutschAnswer]):

    def __init__(self, db: AsyncSession):
        super().__init__(StartDeutschAnswer, db)

    async def bulk_upsert(self, session_id: UUID, answers: list[dict]) -> list[StartDeutschAnswer]:
        """
        Remplace les réponses existantes de la session par les nouvelles
        (une session ne se soumet qu'une fois, mais on reste tolérant à un
        double submit réseau).
        """
        await self.db.execute(
            delete(StartDeutschAnswer).where(StartDeutschAnswer.session_id == session_id)
        )
        instances = [StartDeutschAnswer(session_id=session_id, **a) for a in answers]
        self.db.add_all(instances)
        await self.db.commit()
        for instance in instances:
            await self.db.refresh(instance)
        return instances


class SchreibenCorrectionRepository(BaseRepository[StartDeutschSchreibenCorrection]):

    def __init__(self, db: AsyncSession):
        super().__init__(StartDeutschSchreibenCorrection, db)

    async def get_by_session(self, session_id: UUID) -> list[StartDeutschSchreibenCorrection]:
        result = await self.db.execute(
            select(StartDeutschSchreibenCorrection).where(
                StartDeutschSchreibenCorrection.session_id == session_id
            )
        )
        return list(result.scalars().all())