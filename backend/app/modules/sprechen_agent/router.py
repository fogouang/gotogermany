"""
app/modules/sprechen_agent/router.py
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from fastapi.routing import APIRouter
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import update
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
    SprechenPreviewResponse,
    SprechenPreviewTeil,
    StudentTurnEvent,
)
from .service import SprechenAgentService
from .session_state import SessionState, SessionStatus
from app.modules.exam_access.visibility import can_see_private


router = APIRouter()

_inbound_adapter: TypeAdapter[InboundMessage] = TypeAdapter(InboundMessage)

SPRECHEN_PROVIDERS = {"goethe", "telc", "ösd", "osd", "oesd", "ecl", "testdaf"}

# Temps du Teil écoulé pendant que l'examinatrice parle : on la laisse
# finir sa phrase, mais jamais plus longtemps que ça.
TEIL_TIME_UP_GRACE_SECONDS = 12.0

# Un oral complet avec l'examinatrice coûte 2 crédits IA, débités au
# démarrage réel (premier "Commencer"), remboursés si la toute première
# connexion Live échoue. La lecture du sujet (aperçu) reste gratuite.
SPRECHEN_CREDIT_COST = 2
# Code de fermeture applicatif (plage 4000-4999) : crédits insuffisants
WS_CLOSE_INSUFFICIENT_CREDITS = 4402


# ---------------------------------------------------------------------------
# Chargement du sujet (partagé par la WebSocket et l'aperçu HTTP)
# ---------------------------------------------------------------------------

class _SubjectUnavailable(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


async def load_subject_data(
    db: AsyncSession, subject_id: UUID, user: User
) -> tuple[dict[str, Any], str, str]:
    from app.modules.exams.repository import ExamRepository, LevelRepository, SubjectRepository

    subject = await SubjectRepository(db).get_with_modules(subject_id)

    # Sujet inexistant, ou sujet privé (réservé à la banque des
    # enseignants) ouvert par un non-admin : même réponse, pour ne pas
    # révéler l'existence d'un sujet privé.
    if subject is None or (subject.is_private and not can_see_private(user)):
        raise _SubjectUnavailable("Sujet introuvable.")

    level = await LevelRepository(db).get_by_id_or_404(subject.level_id)
    exam = await ExamRepository(db).get_by_id_or_404(level.exam_id)

    sprechen_module = next(
        (m for m in subject.modules if m.slug in ("sprechen", "muendlicher_ausdruck")),
        None,
    )
    if sprechen_module is None:
        raise _SubjectUnavailable("No Sprechen module for this subject.")

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


async def get_subject_data(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_ws),
) -> tuple[dict[str, Any], str, str]:
    try:
        return await load_subject_data(db, subject_id, current_user)
    except _SubjectUnavailable as exc:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=exc.reason)


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
# Crédits
# ---------------------------------------------------------------------------

def _credits_exempt(user: User) -> bool:
    """Les admins testent sans consommer de crédits."""
    return bool(user.is_admin)


async def _charge_credits(db: AsyncSession, user_id: UUID) -> bool:
    """Débit atomique : ne passe que si le solde suffit encore au moment
    du débit (pas de double débit ni de solde négatif sur un double clic)."""
    result = await db.execute(
        update(User)
        .where(User.id == user_id, User.ai_credits >= SPRECHEN_CREDIT_COST)
        .values(ai_credits=User.ai_credits - SPRECHEN_CREDIT_COST)
        .returning(User.ai_credits)
    )
    remaining = result.scalar_one_or_none()
    await db.commit()
    return remaining is not None


async def _refund_credits(db: AsyncSession, user_id: UUID) -> None:
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(ai_credits=User.ai_credits + SPRECHEN_CREDIT_COST)
    )
    await db.commit()


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
    user: User
    # Set by _relay_client_to_agent() on ReadyToStartMessage; waited on
    # by _relay_agent_to_client() whenever a Teil transition leaves the
    # session in PREPARING with no segment yet open. Recreated (a fresh
    # Event) each time we enter a new preparation phase, so a stale
    # "set" from a previous Teil's prep can never be misread as
    # already-ready for the next one.
    ready_event: asyncio.Event = field(default_factory=asyncio.Event)
    # Heure de fin du Teil en cours (horloge de la boucle asyncio).
    # Fixée à l'envoi de teil_started, en même temps que le chrono
    # affiché côté frontend. None pendant la préparation ou si le Teil
    # n'a pas de durée.
    teil_deadline: float | None = None
    # Crédits déjà débités pour cette session (une seule fois)
    credits_charged: bool = False


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


def _teil_deadline_from_now(session: SessionState) -> float | None:
    """Heure de fin du Teil courant, comptée à partir de maintenant."""
    minutes = session.current_teil().duration_minutes or 0
    if minutes <= 0:
        return None
    return asyncio.get_running_loop().time() + minutes * 60


def _teil_time_is_up(ctx: _ConnectionContext) -> bool:
    return (
        ctx.teil_deadline is not None
        and asyncio.get_running_loop().time() >= ctx.teil_deadline
    )


async def _open_first_segment_of_teil(ctx: _ConnectionContext) -> None:
    """Called by _enter_preparation_phase() once the student signals
    ready. Opens the Live segment, tells the frontend the Teil has
    started, signals whose turn it is."""
    ctx.segment = await ctx.service.begin_live_segment(
        ctx.session, gemini_api_key=ctx.keys.gemini, openai_api_key=ctx.keys.openai
    )
    # Le chrono du Teil démarre ici, au même moment que celui de l'écran
    ctx.teil_deadline = _teil_deadline_from_now(ctx.session)
    await _send_event(ctx.websocket, ctx.service.to_teil_started_event(ctx.session))
    await _send_role_signal(ctx)


async def _start_paid_session(ctx: _ConnectionContext) -> None:
    """Premier "Commencer" de la session : débit des crédits, puis
    ouverture de la première connexion Live. Remboursement si cette
    toute première connexion échoue (l'élève n'a rien pu faire)."""
    exempt = _credits_exempt(ctx.user)
    if not exempt and not await _charge_credits(ctx.service.db, ctx.user.id):
        await ctx.service.abandon_session(ctx.session, None)
        await ctx.websocket.close(
            code=WS_CLOSE_INSUFFICIENT_CREDITS, reason="Credits insuffisants."
        )
        raise _SessionEnded()

    ctx.credits_charged = True
    try:
        await _open_first_segment_of_teil(ctx)
    except live_client.LiveConnectionError:
        if not exempt:
            await _refund_credits(ctx.service.db, ctx.user.id)
        raise


async def _enter_preparation_phase(ctx: _ConnectionContext) -> None:
    """Sends PreparationStartedEvent and blocks until the frontend
    sends ReadyToStartMessage (via _relay_client_to_agent setting
    ctx.ready_event), then opens the Live segment for this Teil."""
    ctx.teil_deadline = None  # pas de chrono pendant la préparation
    ctx.ready_event = asyncio.Event()  # fresh — never reuse a previous Teil's event
    await _send_event(ctx.websocket, ctx.service.to_preparation_started_event(ctx.session))
    await ctx.ready_event.wait()

    if not ctx.credits_charged:
        await _start_paid_session(ctx)
    else:
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


async def _pump_segment_until_turn_end(ctx: _ConnectionContext) -> bool:
    """Relaie les événements du segment Live jusqu'à la fin du tour.

    Retourne True si le temps du Teil est écoulé (le Teil doit être
    clos tout de suite), False pour une fin de tour normale.

    L'attente a une limite : sans elle, un candidat silencieux bloquait
    la boucle indéfiniment et le Teil ne se terminait jamais. Si le
    temps tombe pendant que l'examinatrice parle, on la laisse finir sa
    phrase (TEIL_TIME_UP_GRACE_SECONDS au plus).
    """
    assert ctx.segment is not None
    loop = asyncio.get_running_loop()
    events = ctx.segment.events().__aiter__()
    next_event: asyncio.Task | None = None
    agent_talking = False
    grace_until: float | None = None

    try:
        while True:
            if next_event is None:
                next_event = asyncio.ensure_future(events.__anext__())

            timeout: float | None = None
            if ctx.teil_deadline is not None:
                limit = grace_until if grace_until is not None else ctx.teil_deadline
                timeout = max(0.0, limit - loop.time())

            done, _ = await asyncio.wait({next_event}, timeout=timeout)

            if not done:
                # Heure de fin atteinte sans événement
                if agent_talking and grace_until is None:
                    grace_until = loop.time() + TEIL_TIME_UP_GRACE_SECONDS
                    continue
                return True

            task, next_event = next_event, None
            try:
                event = task.result()
            except StopAsyncIteration:
                # Segment fermé côté fournisseur : même traitement qu'avant
                # (fin de l'async for), sauf si le temps est écoulé.
                return _teil_time_is_up(ctx)

            if event.type == "audio_delta" and event.audio_bytes:
                agent_talking = True
                await ctx.websocket.send_bytes(event.audio_bytes)

            elif event.type == "text_delta" and event.text:
                speaker = event.speaker or "agent"
                await _send_event(
                    ctx.websocket,
                    _transcript_event(ctx.session.session_id, speaker, event.text),
                )
                await ctx.service.record_turn(ctx.session, speaker=speaker, text=event.text)

            elif event.type == "interrupted":
                agent_talking = False

            elif event.type == "turn_complete":
                return _teil_time_is_up(ctx)

            elif event.type == "error":
                raise _LiveProviderError(event.error_message or "unknown Live provider error")
    finally:
        if next_event is not None and not next_event.done():
            next_event.cancel()
            with contextlib.suppress(BaseException):
                await next_event


async def _relay_agent_to_client(ctx: _ConnectionContext) -> None:
    # Entry point: the very first Teil may itself require preparation —
    # sprechen_session_ws() below leaves ctx.segment as None in that
    # case and expects this loop to handle it before doing anything else.
    if ctx.segment is None:
        await _enter_preparation_phase(ctx)

    while True:
        time_up = await _pump_segment_until_turn_end(ctx)

        if time_up:
            # Temps officiel du Teil écoulé : on clôt le Teil, quel que
            # soit le nombre de tours (comme un vrai examinateur).
            transition = await ctx.service.end_teil_now(ctx.session)
        else:
            # Fast, I/O-free: figures out whether the sequence advances and
            # updates session state accordingly. Split out specifically so
            # the role signal below can fire BEFORE the slow Live segment
            # reconnect, not after — see resolve_step_transition()'s
            # docstring for why this fixes the "trou de silence" bug.
            transition = await ctx.service.resolve_step_transition(ctx.session)

        if transition.session_ended:
            await ctx.segment.close()
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

        if transition.teil_changed:
            # New Teil: goes through a preparation phase instead of a
            # segment reconnect — _enter_preparation_phase() already
            # sends PreparationStartedEvent immediately, so there's no
            # silence gap to fix on this path.
            await ctx.segment.close()
            ctx.segment = None
            await _enter_preparation_phase(ctx)
            continue

        # Same Teil continues (same step or the next one in it). Whose
        # turn is next is already fully determined by session state
        # resolve_step_transition() just updated — signal it right now,
        # before paying the reconnect latency, instead of waiting for
        # open_segment_for_current_step() to finish like before.
        await _send_role_signal(ctx)

        old_segment = ctx.segment
        new_segment = await ctx.service.open_segment_for_current_step(
            ctx.session, gemini_api_key=ctx.keys.gemini, openai_api_key=ctx.keys.openai
        )
        await old_segment.close()
        ctx.segment = new_segment


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

    # Premier contrôle, avant toute préparation : solde insuffisant.
    # Le débit réel (atomique) a lieu au premier "Commencer".
    if not _credits_exempt(current_user) and (current_user.ai_credits or 0) < SPRECHEN_CREDIT_COST:
        await websocket.close(code=WS_CLOSE_INSUFFICIENT_CREDITS, reason="Credits insuffisants.")
        return

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
        user=current_user,
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
    except* live_client.LiveConnectionError as eg:
        # live_client.open_segment() already retries with backoff on a
        # connect/handshake failure (see its own docstring) — reaching
        # here means the Live provider stayed unreachable across every
        # retry, not just a passing blip. Ends the session the same
        # clean way a disconnect does, but tells the frontend
        # explicitly (via reason="error") so it can show a real
        # "connection lost" screen instead of just going silent.
        await service.abandon_session(ctx.session, ctx.segment)
        try:
            await ctx.websocket.send_text(
                json.dumps({
                    "type": "session_ended",
                    "session_id": str(ctx.session.session_id),
                    "reason": "error",
                })
            )
        except Exception:  # noqa: BLE001
            pass
        try:
            await ctx.websocket.close(code=1011, reason=str(eg.exceptions[0]))
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# Aperçu d'un sujet : lecture libre, même sans crédit
# ---------------------------------------------------------------------------

@router.get("/subjects/{subject_id}/preview", response_model=SprechenPreviewResponse)
async def get_sprechen_preview(
    subject_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> SprechenPreviewResponse:
    """Même traitement que l'écran de préparation (build_teil_configs) :
    l'élève voit exactement ce qu'il aura en préparation, jamais le
    matériel de l'examinatrice."""
    try:
        subject_raw, provider, level = await load_subject_data(db, subject_id, current_user)
    except _SubjectUnavailable as exc:
        raise HTTPException(status_code=404, detail=exc.reason)

    teile = orchestrator.build_teil_configs(subject_raw, provider)
    raw_max = {t.get("teil_number"): t.get("max_score") for t in subject_raw.get("teile", [])}

    items = [
        SprechenPreviewTeil(
            teil_number=teil.teil_number,
            name=teil.name,
            format_type=teil.format_type,
            instructions=teil.instructions,
            duration_minutes=teil.duration_minutes,
            max_score=raw_max.get(teil.teil_number),
            content_points=teil.content_points,
            themes=teil.themes,
            scenario=teil.scenario,
            stimulus_people=teil.stimulus_people,
            stimulus_text=teil.stimulus_text,
        )
        for teil in teile
    ]

    credits = int(current_user.ai_credits or 0)
    return SprechenPreviewResponse(
        subject_id=subject_id,
        provider=provider,
        level=level,
        total_minutes=sum(t.duration_minutes for t in teile),
        teile=items,
        credit_cost=SPRECHEN_CREDIT_COST,
        credits_available=credits,
        can_start=_credits_exempt(current_user) or credits >= SPRECHEN_CREDIT_COST,
    )


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