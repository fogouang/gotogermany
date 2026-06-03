"""
app/modules/questions/image_service.py

Gestion des images associées aux questions.
Stockage local sous media/images/questions/{question_id}.{ext}
"""
from __future__ import annotations
import shutil
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.questions.repository import QuestionRepository
from app.modules.questions.models import Question
from app.shared.exceptions.http import NotFoundException

MEDIA_ROOT = Path("media/images/questions")


class QuestionImageService:

    def __init__(self, db: AsyncSession):
        self.repo = QuestionRepository(db)

    async def attach_image(
        self,
        question_id: UUID,
        file: UploadFile,
    ) -> Question:
        question = await self.repo.get_by_id_or_404(question_id)

        # Supprimer l'ancienne image si elle existe
        if question.image_file:
            old_path = Path("media") / question.image_file
            if old_path.exists():
                old_path.unlink()

        # Sauvegarder la nouvelle
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        ext       = (file.filename or "img.png").rsplit(".", 1)[-1].lower()
        filename  = f"{question_id}.{ext}"
        dest_path = MEDIA_ROOT / filename

        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Mettre à jour la question
        relative_path = f"images/questions/{filename}"
        return await self.repo.update(question_id, image_file=relative_path)

    async def detach_image(self, question_id: UUID) -> Question:
        question = await self.repo.get_by_id_or_404(question_id)

        if question.image_file:
            path = Path("media") / question.image_file
            if path.exists():
                path.unlink()

        return await self.repo.update(question_id, image_file=None)