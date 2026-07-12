"""
sprechen_agent.service
=========================
SprechenAgentService(db) — same shape as UserService(db) elsewhere in
the codebase: one instance per request/connection, wrapping db for
every method regardless of whether that particular method touches
the database, so router.py always calls through the service
uniformly (`SprechenAgentService(db).start_session(...)`, etc.)

The in-memory Live-session store is the one exception — it's
module-level, not per-instance, because a session must stay
retrievable across whichever request/connection happens to be
handling it, independent of any single db session's lifetime. Redis
was deliberately deferred for V1 (see prior discussion); this is a
plain process-local dict.
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from . import grading, live_client, orchestrator, prompt_builder, repository, schemas
from .session_state import GradingResult, SessionState

# ---------------------------------------------------------------------------
# In-memory session store — process-local, shared across all
# SprechenAgentService instances (module-level, not self.*).
# ---------------------------------------------------------------------------

_SESSION_STORE: dict[UUID, SessionState] = {}
_STORE_LOCK = asyncio.Lock()


class SessionNotFoundError(Exception):
    def __init__(self, session_id: UUID) -> None:
        super().__init__(f"No active session with id {session_id}")
        self.session_id = session_id


async def get_session(session_id: UUID) -> SessionState:
    """Module-level lookup — used by router.py before it has (or
    needs) a SprechenAgentService instance, e.g. to validate a
    session_id on a plain REST endpoint."""
    async with _STORE_LOCK:
        session = _SESSION_STORE.get(session_id)
    if session is None:
        raise SessionNotFoundError(session_id)
    return session


async def _save_session(session: SessionState) -> None:
    async with _STORE_LOCK:
        _SESSION_STORE[session.session_id] = session


async def _forget_session(session_id: UUID) -> None:
    async with _STORE_LOCK:
        _SESSION_STORE.pop(session_id, None)


class SprechenAgentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # -----------------------------------------------------------------
    # Session lifecycle
    # -----------------------------------------------------------------

    async def start_session(
        self,
        *,
        student_id: UUID,
        subject_id: UUID,
        subject_raw: dict[str, Any],
        provider: str,
        level: str,
        gemini_api_key: str,
        openai_api_key: str,
    ) -> tuple[SessionState, live_client.LiveSegment]:
        """Builds the session, opens the first Live segment (Teil 1,
        step 1), and stores it. Returns both so router.py can start
        relaying audio immediately without a second lookup."""
        session = orchestrator.create_session(
            student_id=student_id,
            subject_id=subject_id,
            subject_raw=subject_raw,
            provider=provider,
            level=level,
        )
        session = orchestrator.start_session(session)

        prompt = prompt_builder.build_system_prompt(session, exam_name=provider.capitalize())
        segment = await live_client.open_segment(
            prompt, gemini_api_key=gemini_api_key, openai_api_key=openai_api_key
        )
        session.live_provider = segment.provider

        await _save_session(session)
        return session, segment

    async def record_turn(self, session: SessionState, *, speaker: str, text: str) -> None:
        orchestrator.record_turn(session, speaker=speaker, text=text)
        await _save_session(session)

    async def advance_and_reopen(
        self,
        session: SessionState,
        *,
        gemini_api_key: str,
        openai_api_key: str,
    ) -> tuple[orchestrator.StepTransition, live_client.LiveSegment | None]:
        """Called once a turn boundary is detected. Advances the
        sequence and, unless the session just ended, opens a fresh
        Live segment for the new step — carrying only the text
        transcript forward, never raw audio history."""
        transition = orchestrator.advance(session)
        await _save_session(session)

        if transition.session_ended:
            return transition, None

        prompt = prompt_builder.build_system_prompt(session)
        segment = await live_client.open_segment(
            prompt, gemini_api_key=gemini_api_key, openai_api_key=openai_api_key
        )
        session.live_provider = segment.provider
        await _save_session(session)

        return transition, segment

    async def finalize_session(
        self, session: SessionState, *, anthropic_api_key: str
    ) -> schemas.GradingResponse:
        """Grades the finished session, persists exactly one row via
        self.db, and drops it from the in-memory store."""
        result = await grading.call_claude_grading(session, anthropic_api_key=anthropic_api_key)

        await repository.create_session_result(
            self.db,
            student_id=session.student_id,
            subject_id=session.subject_id,
            provider=session.provider,
            level=session.level,
            teile_breakdown=[t.model_dump() for t in result.teile],
            total_score=result.total_score,
            total_max_score=result.total_max_score,
            passed=result.passed,
            strengths=result.strengths,
            improvement_areas=result.improvement_areas,
            transcript=[e.model_dump() for e in session.transcript],
            live_provider_used=session.live_provider,
            started_at=session.started_at,
        )
        await self.db.commit()
        await _forget_session(session.session_id)

        return self._to_grading_response(result, session)

    async def abandon_session(
        self, session: SessionState, segment: live_client.LiveSegment | None
    ) -> None:
        """Clean disconnect or dropped connection — no grading, no DB
        row (nothing to show for an incomplete attempt)."""
        orchestrator.mark_abandoned(session)
        if segment is not None:
            await segment.close()
        await _forget_session(session.session_id)

    # -----------------------------------------------------------------
    # History
    # -----------------------------------------------------------------

    async def get_history(
        self,
        student_id: UUID,
        *,
        provider: str | None = None,
        level: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[schemas.SessionHistoryItem], int]:
        rows = await repository.get_student_history(
            self.db, student_id, provider=provider, level=level, limit=limit, offset=offset
        )
        total = await repository.count_student_sessions(
            self.db, student_id, provider=provider, level=level
        )
        # NOTE: subject_name left blank — SprechenSession only stores
        # subject_id. Join against the questions module's model here
        # once available without a circular import, or denormalize
        # the subject name onto the row at write time instead.
        items = [
            schemas.SessionHistoryItem(
                session_id=row.id,
                provider=row.provider,
                level=row.level,
                subject_name="",
                total_score=float(row.total_score),
                total_max_score=float(row.total_max_score),
                passed=row.passed,
                completed_at=row.completed_at,
            )
            for row in rows
        ]
        return items, total

    # -----------------------------------------------------------------
    # Domain -> outbound-event adapters (no db needed — staticmethods
    # kept on the class so router.py can call everything through one
    # `service` instance uniformly, matching the rest of the codebase)
    # -----------------------------------------------------------------

    @staticmethod
    def to_session_ready_event(session: SessionState) -> schemas.SessionReadyEvent:
        return schemas.SessionReadyEvent(
            session_id=session.session_id,
            total_teile=len(session.teile),
            first_teil_name=session.teile[0].name,
        )

    @staticmethod
    def to_teil_started_event(session: SessionState) -> schemas.TeilStartedEvent:
        teil = session.current_teil()
        return schemas.TeilStartedEvent(
            session_id=session.session_id,
            teil_number=teil.teil_number,
            teil_name=teil.name,
            instructions=teil.instructions,
            content_points=teil.content_points,
            duration_minutes=teil.duration_minutes,
        )

    @staticmethod
    def _to_grading_response(result: GradingResult, session: SessionState) -> schemas.GradingResponse:
        teil_names = {t.teil_number: t.name for t in session.teile}
        return schemas.GradingResponse(
            session_id=result.session_id,
            provider=result.provider,
            level=result.level,
            teile=[
                schemas.TeilGradingOut(
                    teil_number=t.teil_number,
                    teil_name=teil_names.get(t.teil_number, f"Teil {t.teil_number}"),
                    criteria=[
                        schemas.CriterionScoreOut(
                            criterion_name=c.criterion_name,
                            score=c.score,
                            max_score=c.max_score,
                            comment=c.comment,
                        )
                        for c in t.criteria
                    ],
                    teil_score=t.teil_score,
                    teil_max_score=t.teil_max_score,
                )
                for t in result.teile
            ],
            total_score=result.total_score,
            total_max_score=result.total_max_score,
            passed=result.passed,
            strengths=result.strengths,
            improvement_areas=result.improvement_areas,
            graded_at=result.graded_at,
        )