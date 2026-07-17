"""
sprechen_agent.repository
============================
DB access for SprechenSession. Thin on purpose — no business logic,
no scoring interpretation, just persistence. service.py decides *when*
to call these; grading.py decides *what* the values are.

Assumes async SQLAlchemy 2.0 style (AsyncSession), matching the rest
of your FastAPI stack. Adjust the session dependency import to your
actual `get_db` / `get_async_session` provider.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import SprechenSession


async def create_session_result(
    db: AsyncSession,
    *,
    student_id: uuid.UUID,
    subject_id: uuid.UUID,
    provider: str,
    level: str,
    teile_breakdown: list[dict],
    total_score: float,
    total_max_score: float,
    passed: bool,
    strengths: list[str],
    improvement_areas: list[str],
    transcript: list[dict],
    live_provider_used: str,
    started_at: datetime,
) -> SprechenSession:
    """Persist the one and only row for a completed session. Called
    exactly once by service.py right after grading.py returns."""
    result = SprechenSession(
        student_id=student_id,
        subject_id=subject_id,
        provider=provider,
        level=level,
        teile_breakdown=teile_breakdown,
        total_score=total_score,
        total_max_score=total_max_score,
        passed=passed,
        strengths=strengths,
        improvement_areas=improvement_areas,
        transcript=transcript,
        live_provider_used=live_provider_used,
        started_at=started_at,
    )
    db.add(result)
    await db.flush()   # populate result.id, result.completed_at without committing yet
    return result


async def get_session_by_id(
    db: AsyncSession, session_id: uuid.UUID
) -> SprechenSession | None:
    stmt = select(SprechenSession).where(SprechenSession.id == session_id)
    return await db.scalar(stmt)


async def get_student_history(
    db: AsyncSession,
    student_id: uuid.UUID,
    *,
    provider: str | None = None,
    level: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[SprechenSession]:
    """Past sessions for a student, most recent first. Optional
    provider/level filters match the same filter the subject-picker
    screen already uses, so history can be scoped the same way."""
    stmt = (
        select(SprechenSession)
        .where(SprechenSession.student_id == student_id)
        .order_by(SprechenSession.completed_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if provider is not None:
        stmt = stmt.where(SprechenSession.provider == provider)
    if level is not None:
        stmt = stmt.where(SprechenSession.level == level)

    result = await db.scalars(stmt)
    return list(result.all())


async def count_student_sessions(
    db: AsyncSession,
    student_id: uuid.UUID,
    *,
    provider: str | None = None,
    level: str | None = None,
) -> int:
    """Backs pagination on the history endpoint."""
    stmt = select(func.count()).select_from(SprechenSession).where(
        SprechenSession.student_id == student_id
    )
    if provider is not None:
        stmt = stmt.where(SprechenSession.provider == provider)
    if level is not None:
        stmt = stmt.where(SprechenSession.level == level)

    return (await db.scalar(stmt)) or 0


async def get_latest_session_for_subject(
    db: AsyncSession, student_id: uuid.UUID, subject_id: uuid.UUID
) -> SprechenSession | None:
    """The student's most recent completed attempt on this exact
    subject, if any — used to compute the before/after score delta
    shown after grading. Returns None on a first-ever attempt."""
    stmt = (
        select(SprechenSession)
        .where(
            SprechenSession.student_id == student_id,
            SprechenSession.subject_id == subject_id,
        )
        .order_by(SprechenSession.completed_at.desc())
        .limit(1)
    )
    return await db.scalar(stmt)