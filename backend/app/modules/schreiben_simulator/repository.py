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
        result = SimulatorResult(
            user_id=user_id,
            subject_id=response.subject_id,
            provider=response.provider,
            level=response.level,
            overall_score=response.overall_score,
            max_score=response.max_score,
            passed=response.passed,
            score_percentage=response.score_percentage,
            result_data=response.model_dump(),
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