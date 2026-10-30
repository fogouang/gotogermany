"""
app/modules/exam_access/repository.py
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.exam_access.models import ExamAccess
from app.shared.database.repository import BaseRepository
from app.modules.exams.models import Level


class ExamAccessRepository(BaseRepository[ExamAccess]):

    def __init__(self, db: AsyncSession):
        super().__init__(ExamAccess, db)

    # ── Niveaux du catalogue des examens (B1, B2...) ──

    async def find_by_user_and_level(
        self, user_id: UUID, level_id: UUID
    ) -> ExamAccess | None:
        result = await self.db.execute(
            select(ExamAccess).where(
                ExamAccess.user_id == user_id,
                ExamAccess.level_id == level_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_user_and_level(
        self, user_id: UUID, level_id: UUID
    ) -> ExamAccess | None:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(ExamAccess).where(
                ExamAccess.user_id == user_id,
                ExamAccess.level_id == level_id,
                (ExamAccess.expires_at == None) | (ExamAccess.expires_at > now),
            )
        )
        return result.scalar_one_or_none()

    async def user_has_access(self, user_id: UUID, level_id: UUID) -> bool:
        access = await self.get_active_by_user_and_level(user_id, level_id)
        return access is not None

    # ── Niveaux Start Deutsch ("A1", "A2") ──

    async def find_by_user_and_sd_level(
        self, user_id: UUID, sd_level: str
    ) -> ExamAccess | None:
        result = await self.db.execute(
            select(ExamAccess).where(
                ExamAccess.user_id == user_id,
                ExamAccess.sd_level == sd_level,
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_user_and_sd_level(
        self, user_id: UUID, sd_level: str
    ) -> ExamAccess | None:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(ExamAccess).where(
                ExamAccess.user_id == user_id,
                ExamAccess.sd_level == sd_level,
                (ExamAccess.expires_at == None) | (ExamAccess.expires_at > now),
            )
        )
        return result.scalar_one_or_none()

    async def user_has_sd_access(self, user_id: UUID, sd_level: str) -> bool:
        return await self.get_active_by_user_and_sd_level(user_id, sd_level) is not None

    # ── Listes ──

    async def get_all_by_user(self, user_id: UUID) -> list[ExamAccess]:
        """Tous les accès d'un user avec info exam (Start Deutsch compris)."""
        result = await self.db.execute(
            select(ExamAccess)
            .options(selectinload(ExamAccess.level).selectinload(Level.exam))
            .where(ExamAccess.user_id == user_id)
            .order_by(ExamAccess.granted_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_by_level(self, level_id: UUID) -> list[ExamAccess]:
        result = await self.db.execute(
            select(ExamAccess).where(ExamAccess.level_id == level_id)
        )
        return list(result.scalars().all())