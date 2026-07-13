"""
app/modules/sprechen_agent/router.py

Matches the convention seen in app/modules/users/router.py:
CurrentUser-style typed auth dependencies, get_db from
app.shared.database.session, and a SprechenAgentService(db) instance
per request/connection rather than free functions.

Two concurrent tasks per WebSocket connection:
  - _relay_client_to_agent(): reads frames from the frontend, sends
    audio to the current Live segment, watches for control messages
    (end_turn, abandon_session).
  - _relay_agent_to_client(): reads live_client.LiveSegment.events(),
    forwards audio/transcript to the frontend, and drives session
    transitions (advance, finalize) whenever the Live provider signals
    turn_complete — swapping in a fresh segment mid-connection per the
    segmentation strategy (one Live connection per sequence step).

Resolved against real code shown across this conversation:
  - get_subject_data(): fully confirmed against the real Exam/Level/
    Subject/Module/Teil SQLAlchemy models — see its docstring below.
  - get_live_provider_keys(): confirmed against the real Settings
    class — see its docstring below. One field (OPENAI_API_KEY) still
    needs adding to Settings on your side.

Still open:
  - Settings import path (`app.core.config`) is a guess based on the
    ".env at backend/ root" comment in the Settings file shown —
    confirm the actual module path.
  - Confirm the actual role dependency to use: CurrentUser was assumed
    (any authenticated user), but if Sprechen sessions should be
    restricted to students specifically, swap for a CurrentStudent
    equivalent if one exists alongside CurrentDirector/CurrentSecretary/etc.
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

# ASSUMPTION: import path guessed from the "backend/.env" comment in
# the Settings file shown — adjust if config.py actually lives
# elsewhere (e.g. app/config.py rather than app/core/config.py).
from app.config import Settings, get_settings

from . import live_client, orchestrator
import websockets
from .schemas import (
    AbandonSessionMessage,
    AgentSpeakingEvent,
    InboundMessage,
    OutboundEvent,
    SessionHistoryListResponse,
    StudentTurnEvent,
)
from .service import SprechenAgentService
from .session_state import SessionState

router = APIRouter()

_inbound_adapter: TypeAdapter[InboundMessage] = TypeAdapter(InboundMessage)


# ---------------------------------------------------------------------------
# Dependencies still to wire — see module docstring.
# ---------------------------------------------------------------------------

async def get_subject_data(
    subject_id: UUID, db: AsyncSession = Depends(get_db)
) -> tuple[dict[str, Any], str, str]:
    """Reconstructs the raw Sprechen subject dict this module expects
    from the real Exam -> Level -> Subject -> Module -> Teil hierarchy.

    Fully confirmed against app/modules/exams/models.py,
    repository.py, and service.py — no remaining assumptions:
      - SubjectRepository(db).get_with_modules(subject_id) eager-loads
        Subject -> modules -> teile -> questions in one query.
      - Exam.provider (not .slug) is the "goethe"/"telc"/"oesd" value.
      - Level.cefr_code (not .name) is the bare "B1"/"B2" value.
      - Teil.config is the JSONB blob holding everything variable
        (leitpunkte, scoring_criteria, sprachliche_mittel,
        kandidat_a/kandidat_b, etc.) — Teil has no `name` column, so
        that one comes from config alone. teil_number, format_type,
        instructions, and time_minutes ARE real scalar columns on
        Teil and take precedence over any duplicate value inside
        config, since the columns are the authoritative/queryable
        source and config is the flexible overflow.

    NOTE: the oral module is named "sprechen" for Goethe/ÖSD imports
    but "muendlicher_ausdruck" for TELC imports — same content,
    inconsistent slug from the source JSON. Matched on both until the
    TELC data is renamed at the source.
    """
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
        teil_dict: dict[str, Any] = dict(teil.config or {})
        teil_dict["teil_number"] = teil.teil_number
        teil_dict["format_type"] = teil.format_type
        if teil.instructions is not None:
            teil_dict["instructions"] = teil.instructions
        if teil.time_minutes is not None:
            teil_dict["time_minutes"] = teil.time_minutes
        teil_dict.setdefault("max_score", teil.max_score)
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
    """Confirmed against app/core/config.py's Settings class — GEMINI_API_KEY
    and ANTHROPIC_API_KEY already exist there.

    ONE THING STILL MISSING ON YOUR SIDE: Settings has no OPENAI_API_KEY
    field yet (only AI_PROVIDER/GEMINI_API_KEY/ANTHROPIC_API_KEY, which
    back the *Schreiben* correction provider choice — a separate concern
    from this module's Gemini-primary/OpenAI-fallback Live strategy).
    Add one line to Settings:
        OPENAI_API_KEY: str = ""
    and the .env entry alongside it. Until then, this will raise
    AttributeError the first time a Gemini health-check failure
    actually triggers the OpenAI fallback path in live_client.py.
    """
    return LiveProviderKeys(
        gemini=settings.GEMINI_API_KEY,
        openai=getattr(settings, "OPENAI_API_KEY", ""),  # see docstring — add the real field
        anthropic=settings.ANTHROPIC_API_KEY,
    )


# ---------------------------------------------------------------------------
# Internal signaling exceptions — used to unwind the task group cleanly,
# not user-facing errors.
# ---------------------------------------------------------------------------

class _SessionEnded(Exception):
    pass


class _LiveProviderError(Exception):
    pass


# ---------------------------------------------------------------------------
# Connection context — shared mutable state between the two relay tasks
# ---------------------------------------------------------------------------

@dataclass
class _ConnectionContext:
    websocket: WebSocket
    session: SessionState
    segment: live_client.LiveSegment
    service: SprechenAgentService
    keys: LiveProviderKeys


async def _send_event(websocket: WebSocket, event: OutboundEvent) -> None:
    await websocket.send_text(event.model_dump_json())


async def _send_role_signal(ctx: _ConnectionContext) -> None:
    """Tells the frontend whose turn it is — mirrors the same decision
    service.py makes for trigger_agent_turn(), via the shared
    orchestrator.is_agent_turn_next() helper so the two never drift
    apart."""
    agent_turn_next = orchestrator.is_agent_turn_next(ctx.session)
    event = (
        AgentSpeakingEvent(session_id=ctx.session.session_id)
        if agent_turn_next
        else StudentTurnEvent(session_id=ctx.session.session_id)
    )
    await _send_event(ctx.websocket, event)


def _transcript_event(session_id: UUID, speaker: str, text: str):
    from .schemas import TranscriptUpdateEvent  # local import — avoids widening the module-level import list for one small helper

    return TranscriptUpdateEvent(session_id=session_id, speaker=speaker, text=text)  # type: ignore[arg-type]


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
            try:
                await ctx.segment.send_audio_chunk(raw_bytes)
            except websockets.exceptions.ConnectionClosed:
                # Expected race: a mic chunk in flight right as the
                # Live segment is being swapped/closed for a step
                # transition. Harmless — drop this stray chunk rather
                # than tearing down the whole session over it.
                pass
            continue

        raw_text = message.get("text")
        if raw_text is None:
            continue

        try:
            inbound = _inbound_adapter.validate_python(json.loads(raw_text))
        except (ValidationError, json.JSONDecodeError):
            continue  # ignore malformed control messages rather than killing the session

        if isinstance(inbound, AbandonSessionMessage):
            await ctx.service.abandon_session(ctx.session, ctx.segment)
            await ctx.websocket.close(code=1000)
            raise _SessionEnded()
        # AudioChunkMessage / EndTurnMessage carry no extra action here —
        # audio bytes are relayed above via the binary-frame branch, and
        # end-of-turn is detected server-side by the Live provider's VAD
        # (turn_complete arrives through _relay_agent_to_client instead).


async def _relay_agent_to_client(ctx: _ConnectionContext) -> None:
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
                break  # exit the inner loop; advance the sequence below

            elif event.type == "error":
                raise _LiveProviderError(event.error_message or "unknown Live provider error")

            # "interrupted" (barge-in): no state change needed for V1 —
            # the provider handles clearing its own audio queue.

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

        assert new_segment is not None  # guaranteed by advance_and_reopen's contract
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
    """subject_id lives in the URL (not a first WS message) so every
    dependency — db, the subject lookup — resolves through normal
    FastAPI DI before the socket is even accepted.

    current_user uses get_current_user_ws, NOT the CurrentUser used
    everywhere else in this file — CurrentUser is HTTPBearer-based,
    which requires a Request object and raises
    TypeError: HTTPBearer.__call__() missing 1 required positional
    argument: 'request' on WebSocket routes. get_current_user_ws reads
    the access_token cookie directly off the WebSocket handshake
    instead (the browser sends cookies automatically on the WS
    handshake — no way to set a custom Authorization header from
    browser JS anyway, so cookie-only is correct here, not a
    workaround)."""
    await websocket.accept()

    service = SprechenAgentService(db)
    subject_raw, provider, level = subject_data

    session, segment = await service.start_session(
        student_id=current_user.id,
        subject_id=subject_id,
        subject_raw=subject_raw,
        provider=provider,
        level=level,
        gemini_api_key=keys.gemini,
        openai_api_key=keys.openai,
    )

    ctx = _ConnectionContext(websocket=websocket, session=session, segment=segment, service=service, keys=keys)

    await _send_event(websocket, service.to_session_ready_event(session))
    await _send_event(websocket, service.to_teil_started_event(session))
    await _send_role_signal(ctx)

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(_relay_client_to_agent(ctx))
            tg.create_task(_relay_agent_to_client(ctx))
    except* _SessionEnded:
        pass  # normal completion or explicit abandon — already handled above
    except* WebSocketDisconnect:
        await service.abandon_session(ctx.session, ctx.segment)
    except* _LiveProviderError as eg:
        await service.abandon_session(ctx.session, ctx.segment)
        try:
            await ctx.websocket.close(code=1011, reason=str(eg.exceptions[0]))
        except Exception:  # noqa: BLE001 — best-effort close, connection may already be gone
            pass


# ---------------------------------------------------------------------------
# History — plain REST, no WebSocket involved
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