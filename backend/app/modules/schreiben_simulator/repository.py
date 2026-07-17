"""
app/modules/schreiben_simulator/repository.py
"""
from __future__ import annotations
import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.schreiben_simulator.models import SchreibenSubject, SimulatorResult
from app.modules.schreiben_simulator.schemas import SchreibenSubjectCreate, SchreibenSubjectUpdate, SimulatorCorrectResponse, SimulatorResultResponse

logger = logging.getLogger(__name__)


class SchreibenSubjectRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Lecture ──────────────────────────────────────────

    async def get_all(
        self,
        provider: str | None = None,
        level: str | None = None,
        active_only: bool = True,
    ) -> list[SchreibenSubject]:
        """Lister les sujets avec filtres optionnels."""
        q = select(SchreibenSubject).order_by(
            SchreibenSubject.display_order,
            SchreibenSubject.created_at.desc(),
        )
        if provider:
            q = q.where(SchreibenSubject.provider == provider.lower())
        if level:
            q = q.where(SchreibenSubject.level == level.lower())
        if active_only:
            q = q.where(SchreibenSubject.is_active == True)

        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def get_by_id(self, subject_id: uuid.UUID) -> SchreibenSubject | None:
        result = await self.db.execute(
            select(SchreibenSubject).where(SchreibenSubject.id == subject_id)
        )
        return result.scalar_one_or_none()

    # ── Écriture ─────────────────────────────────────────

    async def create(self, data: SchreibenSubjectCreate) -> SchreibenSubject:
        subject = SchreibenSubject(
            provider=data.provider,
            level=data.level,
            title=data.title,
            description=data.description,
            tasks=[t.model_dump() for t in data.tasks],
            display_order=data.display_order,
            is_active=data.is_active,
        )
        self.db.add(subject)
        await self.db.commit()
        await self.db.refresh(subject)
        logger.info(f"SchreibenSubject créé: {subject.provider.upper()} {subject.level.upper()} — {subject.title}")
        return subject

    async def update(
        self,
        subject_id: uuid.UUID,
        data: SchreibenSubjectUpdate,
    ) -> SchreibenSubject | None:
        subject = await self.get_by_id(subject_id)
        if not subject:
            return None

        if data.title is not None:
            subject.title = data.title
        if data.description is not None:
            subject.description = data.description
        if data.tasks is not None:
            subject.tasks = [t.model_dump() for t in data.tasks]
        if data.display_order is not None:
            subject.display_order = data.display_order
        if data.is_active is not None:
            subject.is_active = data.is_active

        await self.db.commit()
        await self.db.refresh(subject)
        return subject

    async def delete(self, subject_id: uuid.UUID) -> bool:
        subject = await self.get_by_id(subject_id)
        if not subject:
            return False
        await self.db.delete(subject)
        await self.db.commit()
        return True
    
    

    async def save_result(
        self,
        user_id: uuid.UUID,
        response: SimulatorCorrectResponse,
    ) -> SimulatorResult:
        import json

        # Sérialiser en JSON-safe (UUID → str)
        result_data = json.loads(response.model_dump_json())

        result = SimulatorResult(
            user_id=user_id,
            subject_id=response.subject_id,
            provider=response.provider,
            level=response.level,
            overall_score=response.overall_score,
            max_score=response.max_score,
            passed=response.passed,
            score_percentage=response.score_percentage,
            result_data=result_data,
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def get_results_by_user(self, user_id: uuid.UUID) -> list[SimulatorResultResponse]:
        q = (
            select(SimulatorResult, SchreibenSubject.title)
            .join(SchreibenSubject, SimulatorResult.subject_id == SchreibenSubject.id)
            .where(SimulatorResult.user_id == user_id)
            .order_by(SimulatorResult.created_at.desc())
        )
        rows = await self.db.execute(q)
        results = []
        for result, title in rows:
            r = SimulatorResultResponse.model_validate(result)
            r.subject_title = title
            results.append(r)
        return results
    
    
    # ── Lecture depuis la hiérarchie unifiée (Subject/Module/Teil/Question) ──
    # Ajouté en complément de schreiben_subjects — ne remplace rien.
    # Un sujet "unifié" est identifié par le même id que la ligne Subject
    # (donc distinct des UUID de schreiben_subjects, mais du même TYPE),
    # ce qui permet à SchreibenSubjectResponse.id de rester un simple UUID
    # sans distinguer la source à ce niveau.

    async def get_all_unified(
        self, provider: str | None = None, level: str | None = None
    ) -> list[dict]:
        from sqlalchemy.orm import selectinload
        from app.modules.exams.models import Exam, Level, Subject, Module, Teil

        q = (
            select(Subject)
            .join(Level, Level.id == Subject.level_id)
            .join(Exam, Exam.id == Level.exam_id)
            .options(
                selectinload(Subject.modules).selectinload(Module.teile).selectinload(Teil.questions),
                selectinload(Subject.level).selectinload(Level.exam),
            )
            .where(Subject.is_active == True)
        )
        if provider:
            q = q.where(Exam.provider == provider.lower())
        if level:
            q = q.where(Level.cefr_code == level.lower())

        result = await self.db.execute(q)
        subjects = list(result.scalars().unique().all())

        out: list[dict] = []
        for subject in subjects:
            schreiben_module = next(
                (m for m in subject.modules if m.slug == "schreiben"), None
            )
            if schreiben_module is None:
                continue
            built = self._build_unified_subject_dict(subject, schreiben_module)
            if built is not None:
                out.append(built)
        return out


    async def get_by_id_unified(self, subject_id: uuid.UUID) -> dict | None:
        from sqlalchemy.orm import selectinload
        from app.modules.exams.models import Subject, Module, Teil, Level

        result = await self.db.execute(
            select(Subject)
            .options(
                selectinload(Subject.modules).selectinload(Module.teile).selectinload(Teil.questions),
                selectinload(Subject.level).selectinload(Level.exam),
            )
            .where(Subject.id == subject_id)
        )
        subject = result.scalar_one_or_none()
        if subject is None:
            return None

        schreiben_module = next(
            (m for m in subject.modules if m.slug == "schreiben"), None
        )
        if schreiben_module is None:
            return None

        return self._build_unified_subject_dict(subject, schreiben_module)

    @staticmethod
    def _build_unified_subject_dict(subject, schreiben_module) -> dict | None:
        tasks: list[dict] = []
        for teil in sorted(schreiben_module.teile, key=lambda t: t.teil_number):
            question = next(iter(teil.questions), None)
            content = (question.content if question else {}) or {}

            wct = content.get("word_count_target", 150)
            tasks.append({
                "teil": teil.teil_number,
                "scenario": content.get("scenario") or teil.instructions or "",
                "prompts": content.get("prompts", []),
                "topic": content.get("topic", ""),
                "context_ad": content.get("context_ad", ""),
                "opinion_quote": "",  # remplacé par "stimulus" ci-dessous
                "word_count_min": max(wct - 20, 0),
                "word_count_max": wct + 20,
                "word_count_target": wct,
                # Passage direct, sans aplatissement — le frontend sait
                # déjà interpréter cette forme (voir parseStimulus()).
                "stimulus": content.get("stimulus"),
                "stimulus_author": content.get("stimulus_author", ""),
                "themes": content.get("themes"),
                "opinion_variants": content.get("opinion_variants"),
                "stimulus_email": content.get("stimulus_email"),
                "info_comparison": content.get("info_comparison"),
                "leitpunkte": content.get("leitpunkte", []),
                "register": content.get("register", ""),
                "recipient": content.get("recipient", ""),
            })

        if not tasks:
            return None

        return {
            "id": subject.id,
            "provider": subject.level.exam.provider if subject.level and subject.level.exam else "",
            "level": subject.level.cefr_code.lower() if subject.level else "",
            "title": subject.name or f"Sujet {subject.subject_number}",
            "description": None,
            "tasks": tasks,
            "display_order": 0,
            "is_active": subject.is_active,
            "created_at": subject.created_at,
        }