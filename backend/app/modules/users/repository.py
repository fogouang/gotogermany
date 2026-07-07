"""
app/modules/users/repository.py
"""
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User, UserRole
from app.shared.database.repository import BaseRepository
from app.modules.users.models import UserDevice
from app.shared.exceptions.http import ForbiddenException


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def find_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def find_by_verification_token(self, token: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.verification_token == token)
        )
        return result.scalar_one_or_none()

    async def find_by_reset_token(self, token: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.reset_token == token)
        )
        return result.scalar_one_or_none()

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    # ── Licence de centre ─────────────────────

    async def find_students_by_branch(self, branch_id: UUID) -> list[User]:
        from app.modules.users.models import UserRole
        result = await self.db.execute(
            select(User).where(
                User.branch_id == branch_id,
                User.role == UserRole.student,
            )
        )
        return list(result.scalars().all())

    async def find_students_by_center(self, center_id: UUID) -> list[User]:
        from app.modules.users.models import UserRole
        from app.modules.centers.models import Branch
        result = await self.db.execute(
            select(User)
            .join(Branch, Branch.id == User.branch_id)
            .where(
                Branch.center_id == center_id,
                User.role == UserRole.student,
            )
        )
        return list(result.scalars().all())
    
    
    async def find_secretaries_by_center(self, center_id: UUID) -> list[User]:
        from app.modules.centers.models import Branch
        result = await self.db.execute(
            select(User)
            .join(Branch, Branch.id == User.branch_id)
            .where(
                Branch.center_id == center_id,
                User.role == UserRole.branch_secretary,
            )
        )
        return list(result.scalars().all())


class UserDeviceRepository(BaseRepository[UserDevice]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserDevice, db)

    async def register_device_or_raise(self, user_id: UUID, fingerprint: str) -> UserDevice:
        result = await self.db.execute(
            select(UserDevice).where(
                UserDevice.user_id == user_id,
                UserDevice.device_fingerprint == fingerprint,
            )
        )
        existing = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if existing:
            return await self.update(existing.id, last_seen_at=now)
        count_result = await self.db.execute(
            select(UserDevice).where(UserDevice.user_id == user_id)
        )
        current_count = len(list(count_result.scalars().all()))
        if current_count >= 2:
            raise ForbiddenException(
                detail="Ce compte est déjà connecté sur 2 appareils."
            )
        return await self.create(
            user_id=user_id,
            device_fingerprint=fingerprint,
            last_seen_at=now,
        )