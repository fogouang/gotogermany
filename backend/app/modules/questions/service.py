"""
app/modules/questions/service.py
"""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.questions.models import Question
from app.modules.questions.repository import QuestionRepository
from app.modules.questions.schemas import (
    BulkQuestionCreateRequest,
    QuestionCreateRequest,
    QuestionUpdateRequest,
)
from app.modules.exams.repository import TeilRepository
from app.shared.exceptions.http import BadRequestException, NotFoundException


class QuestionService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = QuestionRepository(db)
        self.teil_repo = TeilRepository(db)

    async def get_by_teil(self, teil_id: UUID) -> list[Question]:
        """Liste toutes les questions d'un Teil — vue admin (avec correct_answer)."""
        await self.teil_repo.get_by_id_or_404(teil_id)
        return await self.repo.get_by_teil(teil_id)

    async def get_by_id(self, question_id: UUID) -> Question:
        return await self.repo.get_by_id_or_404(question_id)

    async def create(
        self, teil_id: UUID, data: QuestionCreateRequest
    ) -> Question:
        await self.teil_repo.get_by_id_or_404(teil_id)

        # Vérifier unicité question_number dans ce Teil
        existing = await self.repo.find_by_teil_and_number(
            teil_id, data.question_number
        )
        if existing:
            raise BadRequestException(
                detail=f"La question #{data.question_number} existe déjà dans ce Teil."
            )

        return await self.repo.create(
            teil_id=teil_id,
            **data.model_dump(),
        )

    async def bulk_create(
        self, teil_id: UUID, data: BulkQuestionCreateRequest
    ) -> list[Question]:
        """
        Insère plusieurs questions d'un coup.
        Utilisé par le script d'import.
        """
        await self.teil_repo.get_by_id_or_404(teil_id)

        # Vérifier les doublons dans le payload lui-même
        numbers = [q.question_number for q in data.questions]
        if len(numbers) != len(set(numbers)):
            raise BadRequestException(
                detail="Des numéros de questions sont en doublon dans le payload."
            )

        # Vérifier les doublons avec ce qui existe déjà en BD
        existing = await self.repo.get_by_teil(teil_id)
        existing_numbers = {q.question_number for q in existing}
        conflicts = [n for n in numbers if n in existing_numbers]
        if conflicts:
            raise BadRequestException(
                detail=f"Questions déjà existantes dans ce Teil : {conflicts}"
            )

        questions_data = [
            {"teil_id": teil_id, **q.model_dump()}
            for q in data.questions
        ]
        return await self.repo.bulk_create(questions_data)

    async def update(
        self, question_id: UUID, data: QuestionUpdateRequest
    ) -> Question:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return await self.repo.get_by_id_or_404(question_id)
        return await self.repo.update(question_id, **update_data)

    async def delete(self, question_id: UUID) -> bool:
        return await self.repo.delete(question_id)

    async def replace_teil_questions(
        self, teil_id: UUID, data: BulkQuestionCreateRequest
    ) -> list[Question]:
        """
        Remplace toutes les questions d'un Teil.
        Utile pour re-importer un exam sans conflit.
        """
        await self.teil_repo.get_by_id_or_404(teil_id)
        await self.repo.delete_by_teil(teil_id)

        questions_data = [
            {"teil_id": teil_id, **q.model_dump()}
            for q in data.questions
        ]
        return await self.repo.bulk_create(questions_data)