"""
app/modules/sprechen_agent/router.py
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentUser, get_current_user_ws
from app.modules.users.models import User
from app.shared.database.session import get_db
from app.config import Settings, get_settings

from . import live_client, orchestrator
import websockets
from .schemas import (
    AbandonSessionMessage,
    AgentSpeakingEvent,
    InboundMessage,
    OutboundEvent,
    ReadyToStartMessage,
    SessionHistoryListResponse,
    StudentTurnEvent,
)
from .service import SprechenAgentService
from .session_state import SessionState, SessionStatus

router = APIRouter()

_inbound_adapter: TypeAdapter[InboundMessage] = TypeAdapter(InboundMessage)


# ---------------------------------------------------------------------------
# Dependencies (unchanged from before)
# ---------------------------------------------------------------------------

async def get_subject_data(
    subject_id: UUID, db: AsyncSession = Depends(get_db)
) -> tuple[dict[str, Any], str, str]:
    from app.modules.exams.repository import ExamRepository, LevelRepository, SubjectRepository

    subject = await SubjectRepository(db).get_with_modules(subject_id)
    if subject is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Subject not found.")

    level = await LevelRepository(db).get_by_id_or_404(subject.level_id)
    exam = await ExamRepository(db).get_by_id_or_404(level.exam_id)

    sprechen_module = next(
        (m for m in subject.modules if m.slug in ("sprechen", "muendlicher_ausdruck")),
        None,
    )
    if sprechen_module is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No Sprechen module for this subject.")

    teile_raw: list[dict[str, Any]] = []
    for teil in sprechen_module.teile:
        # Scalar Teil columns first — these ARE real and correctly populated.
        teil_dict: dict[str, Any] = dict(teil.config or {})
        teil_dict["teil_number"] = teil.teil_number
        teil_dict["format_type"] = teil.format_type
        if teil.instructions is not None:
            teil_dict["instructions"] = teil.instructions
        if teil.time_minutes is not None:
            teil_dict["time_minutes"] = teil.time_minutes
        teil_dict.setdefault("max_score", teil.max_score)

        # The actual variable content (leitpunkte/prompts/tasks/
        # scenario/themes/kandidat_a/kandidat_b/scoring_criteria) lives
        # on the Teil's single Question row, NOT on teil.config — that
        # column is only ever populated for images (see
        # image_import_service.py), never for the parsed oral content.
        question = next(iter(teil.questions), None)
        if question is not None:
            teil_dict.update(question.content or {})
            scoring_criteria = (question.correct_answer or {}).get("scoring_criteria")
            if scoring_criteria:
                teil_dict["scoring_criteria"] = scoring_criteria

        teile_raw.append(teil_dict)

    subject_raw: dict[str, Any] = {
        "slug": sprechen_module.slug,
        "max_score": sprechen_module.max_score,
        "time_limit_minutes": sprechen_module.time_limit_minutes,
        "teile": teile_raw,
    }
    return subject_raw, exam.provider, level.cefr_code


@dataclass
class LiveProviderKeys:
    gemini: str
    openai: str
    anthropic: str


def get_live_provider_keys(settings: Settings = Depends(get_settings)) -> LiveProviderKeys:
    return LiveProviderKeys(
        gemini=settings.GEMINI_API_KEY,
        openai=getattr(settings, "OPENAI_API_KEY", ""),
        anthropic=settings.ANTHROPIC_API_KEY,
    )


# ---------------------------------------------------------------------------
# Internal signaling exceptions
# ---------------------------------------------------------------------------

class _SessionEnded(Exception):
    pass


class _LiveProviderError(Exception):
    pass


# ---------------------------------------------------------------------------
# Connection context
# ---------------------------------------------------------------------------

@dataclass
class _ConnectionContext:
    websocket: WebSocket
    session: SessionState
    segment: live_client.LiveSegment | None  # None while PREPARING
    service: SprechenAgentService
    keys: LiveProviderKeys
    # Set by _relay_client_to_agent() on ReadyToStartMessage; waited on
    # by _relay_agent_to_client() whenever a Teil transition leaves the
    # session in PREPARING with no segment yet open. Recreated (a fresh
    # Event) each time we enter a new preparation phase, so a stale
    # "set" from a previous Teil's prep can never be misread as
    # already-ready for the next one.
    ready_event: asyncio.Event


async def _send_event(websocket: WebSocket, event: OutboundEvent) -> None:
    await websocket.send_text(event.model_dump_json())


async def _send_role_signal(ctx: _ConnectionContext) -> None:
    agent_turn_next = orchestrator.is_agent_turn_next(ctx.session)
    event = (
        AgentSpeakingEvent(session_id=ctx.session.session_id)
        if agent_turn_next
        else StudentTurnEvent(session_id=ctx.session.session_id)
    )
    await _send_event(ctx.websocket, event)


def _transcript_event(session_id: UUID, speaker: str, text: str):
    from .schemas import TranscriptUpdateEvent
    return TranscriptUpdateEvent(session_id=session_id, speaker=speaker, text=text)  # type: ignore[arg-type]


async def _open_first_segment_of_teil(ctx: _ConnectionContext) -> None:
    """Shared by the initial connection and by advance_and_reopen()
    when a Teil transition leads into ACTIVE without needing a prep
    wait (preparation_minutes == 0). Opens the Live segment, tells the
    frontend the Teil has started, signals whose turn it is."""
    ctx.segment = await ctx.service.begin_live_segment(
        ctx.session, gemini_api_key=ctx.keys.gemini, openai_api_key=ctx.keys.openai
    )
    await _send_event(ctx.websocket, ctx.service.to_teil_started_event(ctx.session))
    await _send_role_signal(ctx)


async def _enter_preparation_phase(ctx: _ConnectionContext) -> None:
    """Sends PreparationStartedEvent and blocks until the frontend
    sends ReadyToStartMessage (via _relay_client_to_agent setting
    ctx.ready_event), then opens the Live segment for this Teil."""
    ctx.ready_event = asyncio.Event()  # fresh — never reuse a previous Teil's event
    await _send_event(ctx.websocket, ctx.service.to_preparation_started_event(ctx.session))
    await ctx.ready_event.wait()
    await _open_first_segment_of_teil(ctx)


# ---------------------------------------------------------------------------
# Relay tasks
# ---------------------------------------------------------------------------

async def _relay_client_to_agent(ctx: _ConnectionContext) -> None:
    while True:
        message = await ctx.websocket.receive()

        if message.get("type") == "websocket.disconnect":
            raise WebSocketDisconnect()

        raw_bytes = message.get("bytes")
        if raw_bytes is not None:
            if ctx.segment is None:
                # Stray audio arriving during a preparation phase —
                # there's no segment to relay to yet. Drop it silently
                # rather than erroring; the frontend shouldn't be
                # streaming mic audio before ready_to_start anyway.
                continue
            try:
                await ctx.segment.send_audio_chunk(raw_bytes)
            except websockets.exceptions.ConnectionClosed:
                pass
            continue

        raw_text = message.get("text")
        if raw_text is None:
            continue
        print(f"DEBUG received raw text: {raw_text!r}")

        try:
            inbound = _inbound_adapter.validate_python(json.loads(raw_text))
        except (ValidationError, json.JSONDecodeError) as e:
            print(f"DEBUG rejected inbound message: {raw_text!r} -> {e}")
            continue

        if isinstance(inbound, AbandonSessionMessage):
            await ctx.service.abandon_session(ctx.session, ctx.segment)
            await ctx.websocket.close(code=1000)
            raise _SessionEnded()

        if isinstance(inbound, ReadyToStartMessage):
            # Only meaningful while PREPARING; harmless no-op otherwise
            # (e.g. a duplicate click on the frontend's "start" button).
            if ctx.session.status == SessionStatus.PREPARING:
                ctx.ready_event.set()
            continue
        # AudioChunkMessage / EndTurnMessage: no extra action, as before.


async def _relay_agent_to_client(ctx: _ConnectionContext) -> None:
    # Entry point: the very first Teil may itself require preparation —
    # sprechen_session_ws() below leaves ctx.segment as None in that
    # case and expects this loop to handle it before doing anything else.
    if ctx.segment is None:
        await _enter_preparation_phase(ctx)

    while True:
        async for event in ctx.segment.events():
            if event.type == "audio_delta" and event.audio_bytes:
                await ctx.websocket.send_bytes(event.audio_bytes)

            elif event.type == "text_delta" and event.text:
                speaker = event.speaker or "agent"
                await _send_event(
                    ctx.websocket,
                    _transcript_event(ctx.session.session_id, speaker, event.text),
                )
                await ctx.service.record_turn(ctx.session, speaker=speaker, text=event.text)

            elif event.type == "turn_complete":
                break

            elif event.type == "error":
                raise _LiveProviderError(event.error_message or "unknown Live provider error")

        transition, new_segment = await ctx.service.advance_and_reopen(
            ctx.session, gemini_api_key=ctx.keys.gemini, openai_api_key=ctx.keys.openai
        )
        await ctx.segment.close()

        if transition.session_ended:
            response = await ctx.service.finalize_session(
                ctx.session, anthropic_api_key=ctx.keys.anthropic
            )
            await ctx.websocket.send_text(
                json.dumps({"type": "session_ended", "session_id": str(ctx.session.session_id), "reason": "completed"})
            )
            await ctx.websocket.send_text(
                json.dumps({"type": "grading_result", **response.model_dump(mode="json")})
            )
            await ctx.websocket.close(code=1000)
            raise _SessionEnded()

        if new_segment is None:
            # advance_and_reopen() put the session into PREPARING for
            # the new Teil instead of opening a segment — wait for the
            # student, same as the very first Teil.
            ctx.segment = None
            await _enter_preparation_phase(ctx)
            continue

        ctx.segment = new_segment

        if transition.teil_changed:
            await _send_event(ctx.websocket, ctx.service.to_teil_started_event(ctx.session))
        await _send_role_signal(ctx)


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------
@router.websocket("/ws/{subject_id}")
async def sprechen_session_ws(
    websocket: WebSocket,
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_ws),
    keys: LiveProviderKeys = Depends(get_live_provider_keys),
    subject_data: tuple[dict[str, Any], str, str] = Depends(get_subject_data),
) -> None:
    await websocket.accept()

    service = SprechenAgentService(db)
    subject_raw, provider, level = subject_data

    # start_session() now always leaves the session in PREPARING —
    # every Teil (including the first) goes through a preparation
    # screen before its Live segment opens, regardless of what
    # preparation_minutes the subject data has (falls back to a
    # fixed default when absent — see to_preparation_started_event()).
    session = await service.start_session(
        student_id=current_user.id,
        subject_id=subject_id,
        subject_raw=subject_raw,
        provider=provider,
        level=level,
    )

    ctx = _ConnectionContext(
        websocket=websocket,
        session=session,
        segment=None,
        service=service,
        keys=keys,
        ready_event=asyncio.Event(),
    )

    await _send_event(websocket, service.to_session_ready_event(session))

    # No more conditional here — ctx.segment stays None, and
    # _relay_agent_to_client() enters the preparation phase
    # unconditionally on its first iteration (its own
    # `if ctx.segment is None:` check), same as it already does for
    # every subsequent Teil transition.

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(_relay_client_to_agent(ctx))
            tg.create_task(_relay_agent_to_client(ctx))
    except* _SessionEnded:
        pass
    except* WebSocketDisconnect:
        await service.abandon_session(ctx.session, ctx.segment)
    except* _LiveProviderError as eg:
        await service.abandon_session(ctx.session, ctx.segment)
        try:
            await ctx.websocket.close(code=1011, reason=str(eg.exceptions[0]))
        except Exception:  # noqa: BLE001
            pass

# ---------------------------------------------------------------------------
# History — unchanged
# ---------------------------------------------------------------------------

@router.get("/history", response_model=SessionHistoryListResponse)
async def get_sprechen_history(
    current_user: CurrentUser,
    provider: str | None = Query(default=None),
    level: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> SessionHistoryListResponse:
    service = SprechenAgentService(db)
    items, total = await service.get_history(
        current_user.id, provider=provider, level=level, limit=limit, offset=offset
    )
    return SessionHistoryListResponse(items=items, total=total)