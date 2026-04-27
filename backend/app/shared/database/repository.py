"""
app/shared/database/repository.py

Base Repository Pattern pour opérations CRUD génériques.
"""
import app.shared.database.registry
from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.base import Base  
from app.shared.exceptions.base import DatabaseException
from app.shared.exceptions.http import NotFoundException

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repository générique pour opérations CRUD.

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: AsyncSession):
                super().__init__(User, db)

            async def find_by_email(self, email: str) -> User | None:
                result = await self.db.execute(
                    select(User).where(User.email == email)
                )
                return result.scalar_one_or_none()
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, **kwargs):
        try:
            obj = self.model(**kwargs)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            return obj
        except Exception as e:
            await self.db.rollback()
            print(f"❌ DB CREATE ERROR ({self.model.__name__}): {repr(e)}")
            raise DatabaseException(str(e))  # ← str(e) au lieu de ...

    async def get_by_id(self, id: UUID) -> ModelType | None:
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(
                message=f"Erreur lors de la récupération de {self.model.__name__}",
                original_error=e,
            )

    async def get_by_id_or_404(self, id: UUID) -> ModelType:
        instance = await self.get_by_id(id)
        if instance is None:
            raise NotFoundException(
                resource=self.model.__name__,
                identifier=str(id),
            )
        return instance

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        try:
            result = await self.db.execute(
                select(self.model).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            raise DatabaseException(
                message=f"Erreur lors de la récupération de {self.model.__name__}",
                original_error=e,
            )

    async def count(self) -> int:
        try:
            result = await self.db.execute(
                select(func.count()).select_from(self.model)
            )
            return result.scalar_one()
        except Exception as e:
            raise DatabaseException(
                message=f"Erreur lors du comptage de {self.model.__name__}",
                original_error=e,
            )

    async def update(self, id: UUID, **kwargs: Any) -> ModelType:
        try:
            instance = await self.get_by_id_or_404(id)
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await self.db.commit()
            await self.db.refresh(instance)
            return instance
        except NotFoundException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(
                message=f"Erreur lors de la mise à jour de {self.model.__name__}",
                original_error=e,
            )

    async def delete(self, id: UUID) -> bool:
        try:
            instance = await self.get_by_id(id)
            if instance is None:
                return False
            await self.db.delete(instance)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(
                message=f"Erreur lors de la suppression de {self.model.__name__}",
                original_error=e,
            )

    async def exists(self, id: UUID) -> bool:
        instance = await self.get_by_id(id)
        return instance is not None