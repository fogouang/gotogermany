"""
app/modules/questions/repository.py
"""
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.questions.models import Question
from app.shared.database.repository import BaseRepository


class QuestionRepository(BaseRepository[Question]):

    def __init__(self, db: AsyncSession):
        super().__init__(Question, db)

    async def get_by_teil(self, teil_id: UUID) -> list[Question]:
        result = await self.db.execute(
            select(Question)
            .where(Question.teil_id == teil_id)
            .order_by(Question.question_number)
        )
        return list(result.scalars().all())

    async def find_by_teil_and_number(
        self, teil_id: UUID, question_number: int
    ) -> Question | None:
        result = await self.db.execute(
            select(Question).where(
                Question.teil_id == teil_id,
                Question.question_number == question_number,
            )
        )
        return result.scalar_one_or_none()

    async def bulk_create(self, questions: list[dict]) -> list[Question]:
        """
        Insert en masse — pour le script d'import.
        Chaque dict doit contenir tous les champs du modèle.
        """
        instances = [Question(**q) for q in questions]
        self.db.add_all(instances)
        await self.db.commit()
        for instance in instances:
            await self.db.refresh(instance)
        return instances

    async def delete_by_teil(self, teil_id: UUID) -> int:
        """Supprime toutes les questions d'un Teil. Retourne le nombre supprimé."""
        result = await self.db.execute(
            delete(Question).where(Question.teil_id == teil_id)
        )
        await self.db.commit()
        return result.rowcount