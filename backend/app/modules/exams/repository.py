"""
app/modules/exams/repository.py
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.exams.models import Exam, Level, Subject, Module, Teil
from app.shared.database.repository import BaseRepository


class ExamRepository(BaseRepository[Exam]):

    def __init__(self, db: AsyncSession):
        super().__init__(Exam, db)

    async def find_by_slug(self, slug: str) -> Exam | None:
        result = await self.db.execute(
            select(Exam).where(Exam.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Exam]:
        result = await self.db.execute(
            select(Exam).where(Exam.is_active == True).order_by(Exam.provider)
        )
        return list(result.scalars().all())

    async def get_with_levels(self, exam_id: UUID) -> Exam | None:
        result = await self.db.execute(
            select(Exam)
            .options(selectinload(Exam.levels))
            .where(Exam.id == exam_id)
        )
        return result.scalar_one_or_none()

    async def get_full(self, exam_id: UUID) -> Exam | None:
        """Exam + levels + subjects + modules + teile + questions."""
        result = await self.db.execute(
            select(Exam)
            .options(
                selectinload(Exam.levels)
                .selectinload(Level.subjects)
                .selectinload(Subject.modules)
                .selectinload(Module.teile)
                .selectinload(Teil.questions)  # ← questions incluses
            )
            .where(Exam.id == exam_id)
        )
        return result.scalar_one_or_none()

    async def get_full_by_slug(self, slug: str) -> Exam | None:
        result = await self.db.execute(
            select(Exam)
            .options(
                selectinload(Exam.levels)
                .selectinload(Level.subjects)
                .selectinload(Subject.modules)
                .selectinload(Module.teile)
                .selectinload(Teil.questions)  # ← questions incluses
            )
            .where(Exam.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all_with_levels(self) -> list[Exam]:
        result = await self.db.execute(
            select(Exam)
            .options(selectinload(Exam.levels))
            .where(Exam.is_active == True)
            .order_by(Exam.provider)
        )
        return list(result.scalars().all())


class LevelRepository(BaseRepository[Level]):

    def __init__(self, db: AsyncSession):
        super().__init__(Level, db)

    async def get_by_exam(self, exam_id: UUID) -> list[Level]:
        result = await self.db.execute(
            select(Level)
            .where(Level.exam_id == exam_id)
            .order_by(Level.display_order)
        )
        return list(result.scalars().all())

    async def get_free_levels(self) -> list[Level]:
        result = await self.db.execute(
            select(Level).where(Level.is_free == True)
        )
        return list(result.scalars().all())

    async def get_with_subjects(self, level_id: UUID) -> Level | None:
        """Level + subjects + modules + teile + questions."""
        result = await self.db.execute(
            select(Level)
            .options(
                selectinload(Level.subjects)
                .selectinload(Subject.modules)
                .selectinload(Module.teile)
                .selectinload(Teil.questions)  # ← questions incluses
            )
            .where(Level.id == level_id)
        )
        return result.scalar_one_or_none()


class SubjectRepository(BaseRepository[Subject]):

    def __init__(self, db: AsyncSession):
        super().__init__(Subject, db)

    async def get_by_level(self, level_id: UUID) -> list[Subject]:
        result = await self.db.execute(
            select(Subject)
            .where(Subject.level_id == level_id, Subject.is_active == True)
            .order_by(Subject.subject_number)
        )
        return list(result.scalars().all())

    async def get_next_number(self, level_id: UUID) -> int:
        subjects = await self.get_by_level(level_id)
        return max((s.subject_number for s in subjects), default=0) + 1

    async def get_with_modules(self, subject_id: UUID) -> Subject | None:
        """Subject + modules + teile + questions."""
        result = await self.db.execute(
            select(Subject)
            .options(
                selectinload(Subject.modules)
                .selectinload(Module.teile)
                .selectinload(Teil.questions)  # ← questions incluses
            )
            .where(Subject.id == subject_id)
        )
        return result.scalar_one_or_none()


class ModuleRepository(BaseRepository[Module]):

    def __init__(self, db: AsyncSession):
        super().__init__(Module, db)

    async def get_by_subject(self, subject_id: UUID) -> list[Module]:
        result = await self.db.execute(
            select(Module)
            .where(Module.subject_id == subject_id)
            .order_by(Module.display_order)
        )
        return list(result.scalars().all())


class TeilRepository(BaseRepository[Teil]):

    def __init__(self, db: AsyncSession):
        super().__init__(Teil, db)

    async def get_by_module(self, module_id: UUID) -> list[Teil]:
        result = await self.db.execute(
            select(Teil)
            .where(Teil.module_id == module_id)
            .order_by(Teil.teil_number)
        )
        return list(result.scalars().all())