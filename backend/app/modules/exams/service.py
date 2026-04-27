"""
app/modules/exams/service.py
"""
from uuid import UUID

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.exams.models import Exam, Level, Subject, Module, Teil
from app.modules.exams.repository import (
    ExamRepository, LevelRepository, SubjectRepository,
    ModuleRepository, TeilRepository,
)
from app.modules.exams.schemas import (
    ExamCreateRequest, ExamUpdateRequest,
    LevelCreateRequest, LevelUpdateRequest,
    SubjectCreateRequest, SubjectUpdateRequest,
    SubjectResponse,
    ModuleCreateRequest, TeilCreateRequest,
)
from app.shared.exceptions.http import BadRequestException, NotFoundException


class ExamService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExamRepository(db)
        self.level_repo = LevelRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.module_repo = ModuleRepository(db)
        self.teil_repo = TeilRepository(db)

    # ── Exams ────────────────────────────────────────────

    async def get_catalog(self) -> list[Exam]:
        return await self.repo.get_all_with_levels()

    async def get_detail(self, exam_id: UUID) -> Exam:
        exam = await self.repo.get_full(exam_id)
        if not exam:
            raise NotFoundException(resource="Exam", identifier=str(exam_id))
        return exam

    async def get_by_slug(self, slug: str) -> Exam:
        exam = await self.repo.get_full_by_slug(slug)
        if not exam:
            raise NotFoundException(resource="Exam", identifier=slug)
        return exam

    async def create(self, data: ExamCreateRequest) -> Exam:
        existing = await self.repo.find_by_slug(data.slug)
        if existing:
            raise BadRequestException(
                detail=f"Un exam avec le slug '{data.slug}' existe déjà."
            )
        return await self.repo.create(**data.model_dump())

    async def update(self, exam_id: UUID, data: ExamUpdateRequest) -> Exam:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return await self.repo.get_by_id_or_404(exam_id)
        return await self.repo.update(exam_id, **update_data)

    async def delete(self, exam_id: UUID) -> bool:
        return await self.repo.delete(exam_id)

    # ── Levels ───────────────────────────────────────────

    async def get_levels(self, exam_id: UUID) -> list[Level]:
        await self.repo.get_by_id_or_404(exam_id)
        return await self.level_repo.get_by_exam(exam_id)

    async def create_level(self, exam_id: UUID, data: LevelCreateRequest) -> Level:
        await self.repo.get_by_id_or_404(exam_id)
        existing = await self.level_repo.get_by_exam(exam_id)
        if any(l.cefr_code == data.cefr_code for l in existing):
            raise BadRequestException(
                detail=f"Le level '{data.cefr_code}' existe déjà pour cet exam."
            )
        return await self.level_repo.create(exam_id=exam_id, **data.model_dump())

    async def update_level(self, level_id: UUID, data: LevelUpdateRequest) -> Level:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return await self.level_repo.get_by_id_or_404(level_id)
        return await self.level_repo.update(level_id, **update_data)

    async def delete_level(self, level_id: UUID) -> bool:
        return await self.level_repo.delete(level_id)

    # ── Subjects ─────────────────────────────────────────

    async def get_subjects(self, level_id: UUID) -> list[SubjectResponse]:
        """Retourne les sujets avec has_audio calculé."""
        await self.level_repo.get_by_id_or_404(level_id)
        subjects = await self.subject_repo.get_by_level(level_id)

        from app.modules.questions.models import Question

        result_list = []
        for subject in subjects:
            # Vérifier si au moins une question de ce sujet a un audio_file
            has_audio_result = await self.db.execute(
                select(
                    exists().where(
                        Question.audio_file.isnot(None),
                        Question.teil_id.in_(
                            select(Teil.id)
                            .join(Module, Module.id == Teil.module_id)
                            .where(Module.subject_id == subject.id)
                        )
                    )
                )
            )
            has_audio = has_audio_result.scalar() or False

            result_list.append(SubjectResponse(
                id=subject.id,
                level_id=subject.level_id,
                subject_number=subject.subject_number,
                name=subject.name,
                is_active=subject.is_active,
                has_audio=has_audio,
            ))

        return result_list

    async def create_subject(self, level_id: UUID, data: SubjectCreateRequest) -> Subject:
        await self.level_repo.get_by_id_or_404(level_id)
        next_number = await self.subject_repo.get_next_number(level_id)
        return await self.subject_repo.create(
            level_id=level_id,
            subject_number=next_number,
            name=data.name or f"Sujet {next_number}",
            is_active=data.is_active,
        )

    async def update_subject(self, subject_id: UUID, data: SubjectUpdateRequest) -> Subject:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return await self.subject_repo.get_by_id_or_404(subject_id)
        return await self.subject_repo.update(subject_id, **update_data)

    async def delete_subject(self, subject_id: UUID) -> bool:
        return await self.subject_repo.delete(subject_id)

    # ── Modules ──────────────────────────────────────────

    async def get_modules(self, subject_id: UUID) -> list[Module]:
        await self.subject_repo.get_by_id_or_404(subject_id)
        return await self.module_repo.get_by_subject(subject_id)

    async def create_module(self, subject_id: UUID, data: ModuleCreateRequest) -> Module:
        await self.subject_repo.get_by_id_or_404(subject_id)
        return await self.module_repo.create(subject_id=subject_id, **data.model_dump())

    async def delete_module(self, module_id: UUID) -> bool:
        return await self.module_repo.delete(module_id)

    # ── Teile ────────────────────────────────────────────

    async def get_teile(self, module_id: UUID) -> list[Teil]:
        await self.module_repo.get_by_id_or_404(module_id)
        return await self.teil_repo.get_by_module(module_id)

    async def create_teil(self, module_id: UUID, data: TeilCreateRequest) -> Teil:
        await self.module_repo.get_by_id_or_404(module_id)
        return await self.teil_repo.create(module_id=module_id, **data.model_dump())

    async def delete_teil(self, teil_id: UUID) -> bool:
        return await self.teil_repo.delete(teil_id)