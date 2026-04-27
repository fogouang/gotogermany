"""
app/modules/users/service.py
"""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserChangePasswordRequest, UserUpdateRequest
from app.shared.exceptions.http import BadRequestException, ForbiddenException
from app.shared.security.password import hash_password, verify_password


class UserService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def get_me(self, current_user: User) -> User:
        """Retourne l'utilisateur courant — déjà résolu par la dependency."""
        return current_user

    async def update_me(self, current_user: User, data: UserUpdateRequest) -> User:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return current_user
        return await self.repo.update(current_user.id, **update_data)

    async def change_password(
        self, current_user: User, data: UserChangePasswordRequest
    ) -> User:
        if not verify_password(data.current_password, current_user.hashed_password):
            raise BadRequestException(detail="Mot de passe actuel incorrect.")

        if data.current_password == data.new_password:
            raise BadRequestException(
                detail="Le nouveau mot de passe doit être différent de l'actuel."
            )

        return await self.repo.update(
            current_user.id,
            hashed_password=hash_password(data.new_password),
        )

    # ── Admin ────────────────────────────────────────────

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return list(await self.repo.get_all(skip=skip, limit=limit))

    async def get_by_id(self, user_id: UUID) -> User:
        return await self.repo.get_by_id_or_404(user_id)

    async def toggle_active(self, user_id: UUID, current_user: User) -> User:
        """Active ou désactive un compte utilisateur."""
        if current_user.id == user_id:
            raise BadRequestException(detail="Vous ne pouvez pas désactiver votre propre compte.")

        user = await self.repo.get_by_id_or_404(user_id)
        return await self.repo.update(user_id, is_active=not user.is_active)

    async def delete(self, user_id: UUID, current_user: User) -> bool:
        if current_user.id == user_id:
            raise BadRequestException(detail="Vous ne pouvez pas supprimer votre propre compte.")
        return await self.repo.delete(user_id)