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
was deliberately deferred for V1; this is a plain process-local dict.
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from . import grading, live_client, orchestrator, prompt_builder, repository, schemas
from .session_state import GradingResult, SessionState, SessionStatus

# ---------------------------------------------------------------------------
# In-memory session store — process-local, shared across all
# SprechenAgentService instances (module-level, not self.*).
# ---------------------------------------------------------------------------

_SESSION_STORE: dict[UUID, SessionState] = {}
_STORE_LOCK = asyncio.Lock()

DEFAULT_PREPARATION_MINUTES = 3


class SessionNotFoundError(Exception):
    def __init__(self, session_id: UUID) -> None:
        super().__init__(f"No active session with id {session_id}")
        self.session_id = session_id


async def get_session(session_id: UUID) -> SessionState:
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
    ) -> SessionState:
        """Builds the session only. Does NOT open a Live segment —
        call begin_live_segment() next, either immediately (no prep
        needed) or after the frontend sends ReadyToStartMessage."""
        session = orchestrator.create_session(
            student_id=student_id,
            subject_id=subject_id,
            subject_raw=subject_raw,
            provider=provider,
            level=level,
        )
        first_teil = session.teile[0]
        session.status = (
            SessionStatus.PREPARING if first_teil.preparation_minutes > 0 else SessionStatus.PENDING
        )
        session.status = SessionStatus.PREPARING
        await _save_session(session)
        return session

    async def begin_live_segment(
        self,
        session: SessionState,
        *,
        gemini_api_key: str,
        openai_api_key: str,
    ) -> live_client.LiveSegment:
        """Actually opens the first (or next, mid-session) Live
        segment. Called right after start_session() when there's no
        prep, or after ReadyToStartMessage when there was one."""
        if session.status in (SessionStatus.PENDING, SessionStatus.PREPARING):
            session = orchestrator.start_session(session)

        prompt = prompt_builder.build_system_prompt(session, exam_name=session.provider.capitalize())
        segment = await live_client.open_segment(
            prompt, gemini_api_key=gemini_api_key, openai_api_key=openai_api_key
        )
        session.live_provider = segment.provider
        session.status = SessionStatus.ACTIVE

        if orchestrator.is_agent_turn_next(session):
            await segment.trigger_agent_turn()

        await _save_session(session)
        return segment

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
        """Called once a turn boundary is detected. A fresh Live
        segment is opened every time regardless (cost/segmentation
        strategy), but the SEQUENCE only advances once
        orchestrator.is_step_complete() says this step has had enough
        turns (min_turns).

        Returns (transition, None) in two distinct cases the caller
        must tell apart itself: session_ended (nothing more to do), or
        teil_changed — every Teil change now enters a preparation phase
        unconditionally (router.py must wait for ReadyToStartMessage
        before calling begin_live_segment()), regardless of whether the
        subject data has a real preparation_minutes value. See
        to_preparation_started_event() for the fallback duration used
        when the data doesn't specify one."""
        orchestrator.record_step_turn(session)

        if not orchestrator.is_step_complete(session):
            prompt = prompt_builder.build_system_prompt(session)
            segment = await live_client.open_segment(
                prompt, gemini_api_key=gemini_api_key, openai_api_key=openai_api_key
            )
            session.live_provider = segment.provider

            if orchestrator.is_agent_turn_next(session):
                await segment.trigger_agent_turn()

            await _save_session(session)

            transition = orchestrator.StepTransition(
                teil_changed=False,
                session_ended=False,
                requires_new_live_segment=True,
                new_step=session.current_step(),
            )
            return transition, segment

        transition = orchestrator.advance(session)
        await _save_session(session)

        if transition.session_ended:
            return transition, None

        if transition.teil_changed:
            # Every Teil transition now goes through a preparation phase —
            # the student reviews the new Teil's subject/instructions and
            # explicitly signals ready, exactly like the first Teil at
            # session start. No condition on preparation_minutes anymore:
            # that field is currently never populated in the DB, so
            # gating on it would mean this phase never triggers in
            # practice.
            session.status = SessionStatus.PREPARING
            await _save_session(session)
            return transition, None  # router.py sends PreparationStartedEvent and waits

        prompt = prompt_builder.build_system_prompt(session)
        segment = await live_client.open_segment(
            prompt, gemini_api_key=gemini_api_key, openai_api_key=openai_api_key
        )
        session.live_provider = segment.provider

        if orchestrator.is_agent_turn_next(session):
            await segment.trigger_agent_turn()

        await _save_session(session)

        return transition, segment

    async def _get_previous_attempt_score(
        self, *, student_id: UUID, subject_id: UUID
    ) -> float | None:
        """Best-effort lookup of the student's most recent prior attempt
        on this exact subject, for a simple before/after delta. None if
        this is the student's first time on this subject."""
        previous = await repository.get_latest_session_for_subject(
            self.db, student_id, subject_id
        )
        if previous is None or previous.total_max_score <= 0:
            return None
        return float(previous.total_score) / float(previous.total_max_score) * 100

    async def finalize_session(
        self, session: SessionState, *, anthropic_api_key: str
    ) -> schemas.GradingResponse:
        """Grades the finished session, persists exactly one row via
        self.db, and drops it from the in-memory store."""
        result = await grading.call_claude_grading(session, anthropic_api_key=anthropic_api_key)

        previous_score_percent = await self._get_previous_attempt_score(
            student_id=session.student_id,
            subject_id=session.subject_id,
        )

        await repository.create_session_result(
            self.db,
            student_id=session.student_id,
            subject_id=session.subject_id,
            provider=session.provider,
            level=session.level,
            teile_breakdown=[t.model_dump(mode="json") for t in result.teile],
            total_score=result.total_score,
            total_max_score=result.total_max_score,
            passed=result.passed,
            strengths=result.strengths,
            improvement_areas=result.improvement_areas,
            transcript=[e.model_dump(mode="json") for e in session.transcript],
            live_provider_used=session.live_provider,
            started_at=session.started_at,
        )
        await self.db.commit()
        await _forget_session(session.session_id)

        return self._to_grading_response(result, session, previous_score_percent)

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
    # Domain -> outbound-event adapters
    # -----------------------------------------------------------------

    @staticmethod
    def to_session_ready_event(session: SessionState) -> schemas.SessionReadyEvent:
        return schemas.SessionReadyEvent(
            session_id=session.session_id,
            total_teile=len(session.teile),
            first_teil_name=session.teile[0].name,
        )

    @staticmethod
    def to_preparation_started_event(session: SessionState) -> schemas.PreparationStartedEvent:
        teil = session.current_teil()
        return schemas.PreparationStartedEvent(
            session_id=session.session_id,
            teil_number=teil.teil_number,
            teil_name=teil.name,
            instructions=teil.instructions,
            content_points=teil.content_points,
            themes=teil.themes,
            preparation_minutes=teil.preparation_minutes or DEFAULT_PREPARATION_MINUTES,
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
            themes=teil.themes,
            duration_minutes=teil.duration_minutes,
            preparation_minutes=teil.preparation_minutes or DEFAULT_PREPARATION_MINUTES,
        )

    @staticmethod
    def _to_grading_response(
        result: GradingResult,
        session: SessionState,
        previous_score_percent: float | None = None,
    ) -> schemas.GradingResponse:
        teil_names = {t.teil_number: t.name for t in session.teile}
        current_percent = (
            result.total_score / result.total_max_score * 100 if result.total_max_score else 0.0
        )
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
                            issue=c.issue,
                            model_phrase=c.model_phrase,
                            tip=c.tip,
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
            previous_score_percent=previous_score_percent,
            score_delta_percent=(
                current_percent - previous_score_percent
                if previous_score_percent is not None
                else None
            ),
        )