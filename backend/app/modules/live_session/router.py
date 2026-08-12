"""
app/modules/live_session/router.py

Pont audio WebSocket entre un candidat et un examinateur humain (mode
"live_examiner" du Sprechen). Ne fait AUCUN appel a un LLM/Live provider —
relais brut de bytes audio entre les deux WebSocket connectees a la meme
LiveSession. Remplace, pour ce mode, le point ou sprechen_agent/router.py
appelle Gemini Live.

Ne touche pas au module sprechen_agent existant (mode solo IA) — fichier
entierement separe.

Chat texte (ajout) : relais brut "chat_message" entre les deux WebSocket,
EXACTEMENT comme l'audio/vidéo — aucune persistance en DB, les messages
ne servent que pendant l'appel en cours et disparaissent avec lui.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentUser, get_current_user_ws
from app.modules.users.models import User
from app.shared.database.session import get_db

from .schemas import (
    CreateLiveSessionRequest,
    LiveSessionListResponse,
    LiveSessionResponse,
    SubjectContentResponse,
    SubmitNotesRequest,
)
from .service import LiveSessionService

router = APIRouter()


class _SessionEnded(Exception):
    pass


@dataclass
class _Bridge:
    """
    Etat partage d'une LiveSession en cours, le temps que les deux parties
    soient connectees — vit en memoire process, pas en base.

    Suppose un seul worker/process (coherent avec le deploiement Docker
    Compose actuel, un seul conteneur backend). Si un jour plusieurs
    workers/instances sont necessaires, remplacer ce dict en memoire par
    un relais Redis pub/sub — mais inutile de complexifier avant d'en
    avoir besoin.
    """
    student_ws: WebSocket | None = None
    examiner_ws: WebSocket | None = None


_bridges: dict[UUID, _Bridge] = {}


def _get_or_create_bridge(live_session_id: UUID) -> _Bridge:
    if live_session_id not in _bridges:
        _bridges[live_session_id] = _Bridge()
    return _bridges[live_session_id]


def _cleanup_bridge(live_session_id: UUID, bridge: _Bridge) -> None:
    """Supprime le bridge de la memoire une fois que plus personne n'est connecte."""
    if bridge.student_ws is None and bridge.examiner_ws is None:
        _bridges.pop(live_session_id, None)


async def _notify_peer_left(peer_ws: WebSocket | None) -> None:
    if peer_ws is None:
        return
    try:
        await peer_ws.send_text(json.dumps({"type": "peer_left"}))
    except Exception:  # noqa: BLE001
        pass


async def _relay_chat_message(peer_ws: WebSocket | None, text: str, sender_role: str) -> None:
    """Relais brut, pas de persistance — les messages n'existent que le
    temps de l'appel, exactement comme les octets audio/vidéo."""
    if peer_ws is None or not text:
        return
    try:
        await peer_ws.send_text(json.dumps({"type": "chat_message", "text": text, "from": sender_role}))
    except Exception:  # noqa: BLE001
        pass


# ---------------------------------------------------------------------------
# Endpoint candidat
# ---------------------------------------------------------------------------

@router.websocket("/ws/{live_session_id}/student")
async def live_session_student_ws(
    websocket: WebSocket,
    live_session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_ws),
) -> None:
    service = LiveSessionService(db)
    session = await service.get_or_404(live_session_id)
    if session.student_id != current_user.id:
        await websocket.close(code=4403)
        return

    await websocket.accept()
    bridge = _get_or_create_bridge(live_session_id)
    bridge.student_ws = websocket

    # Le chrono de prépa démarre à la connexion du candidat — waiting -> preparing
    await service.mark_preparing(live_session_id)

    # Prepa unique 20min/3 Teile — pas de decoupage par Teil ici, contrairement
    # au mode IA. duration_minutes en dur pour l'instant ; a terme pourrait
    # venir du sujet, une fois le fix du prep_period unifie fait cote contenu.
    # ⚠️ TEMPORAIRE POUR TEST : 1 au lieu de 20 — remettre à 20 avant la prod !
    await websocket.send_text(json.dumps({"type": "preparation_started", "duration_minutes": 1}))

    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                raise WebSocketDisconnect()

            raw_bytes = message.get("bytes")
            if raw_bytes is not None:
                if bridge.examiner_ws is not None:
                    try:
                        await bridge.examiner_ws.send_bytes(raw_bytes)
                    except Exception:  # noqa: BLE001
                        pass
                continue

            raw_text = message.get("text")
            if raw_text is None:
                continue
            try:
                payload = json.loads(raw_text)
            except json.JSONDecodeError:
                continue

            msg_type = payload.get("type")
            if msg_type == "ready_to_start":
                await service.mark_live(live_session_id)
                live_started_msg = json.dumps({"type": "live_started"})
                # Envoyer au candidat lui-même ET à l'examinateur — sans ça,
                # seul l'examinateur passe en "live" côté client, le
                # candidat reste bloqué sur l'écran de prépa.
                await websocket.send_text(live_started_msg)
                if bridge.examiner_ws is not None:
                    await bridge.examiner_ws.send_text(live_started_msg)
            elif msg_type == "chat_message":
                await _relay_chat_message(bridge.examiner_ws, payload.get("text", ""), "student")
            elif msg_type == "end_session":
                await service.mark_ended(live_session_id)
                raise _SessionEnded()

    except (_SessionEnded, WebSocketDisconnect):
        await _notify_peer_left(bridge.examiner_ws)
        await service.mark_ended(live_session_id)
    finally:
        bridge.student_ws = None
        _cleanup_bridge(live_session_id, bridge)


# ---------------------------------------------------------------------------
# Endpoint examinateur
# ---------------------------------------------------------------------------

@router.websocket("/ws/{live_session_id}/examiner")
async def live_session_examiner_ws(
    websocket: WebSocket,
    live_session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_ws),
) -> None:
    service = LiveSessionService(db)
    session = await service.get_or_404(live_session_id)
    if session.examiner_id != current_user.id:
        await websocket.close(code=4403)
        return

    await websocket.accept()
    bridge = _get_or_create_bridge(live_session_id)
    bridge.examiner_ws = websocket

    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                raise WebSocketDisconnect()

            raw_bytes = message.get("bytes")
            if raw_bytes is not None:
                if bridge.student_ws is not None:
                    try:
                        await bridge.student_ws.send_bytes(raw_bytes)
                    except Exception:  # noqa: BLE001
                        pass
                continue

            raw_text = message.get("text")
            if raw_text is None:
                continue
            try:
                payload = json.loads(raw_text)
            except json.JSONDecodeError:
                continue

            msg_type = payload.get("type")
            if msg_type == "end_session":
                await service.mark_ended(live_session_id)
                raise _SessionEnded()
            elif msg_type == "chat_message":
                await _relay_chat_message(bridge.student_ws, payload.get("text", ""), "examiner")

    except (_SessionEnded, WebSocketDisconnect):
        await _notify_peer_left(bridge.student_ws)
        await service.mark_ended(live_session_id)
    finally:
        bridge.examiner_ws = None
        _cleanup_bridge(live_session_id, bridge)


# ---------------------------------------------------------------------------
# Endpoints REST
# ---------------------------------------------------------------------------

@router.post("", response_model=LiveSessionResponse)
async def create_live_session(
    payload: CreateLiveSessionRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> LiveSessionResponse:
    """Lancée par l'examinateur (staff du centre) — vérifie rôle,
    appartenance au même centre, et que le sujet a bien un module Sprechen."""
    service = LiveSessionService(db)
    session = await service.create_session(
        examiner_id=current_user.id,
        student_id=payload.student_id,
        subject_id=payload.subject_id,
    )
    return await service.to_response(session)


@router.patch("/{live_session_id}/notes", response_model=LiveSessionResponse)
async def submit_examiner_notes(
    live_session_id: UUID,
    payload: SubmitNotesRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> LiveSessionResponse:
    """L'examinateur rédige/complète ses notes — pendant ou après la
    session. Visibles côté student dès que la session est "ended"."""
    service = LiveSessionService(db)
    session = await service.submit_notes(
        live_session_id=live_session_id,
        examiner_id=current_user.id,
        notes=payload.notes,
    )
    return await service.to_response(session)


@router.get("/mine", response_model=LiveSessionListResponse)
async def get_my_live_sessions(
    current_user: CurrentUser,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> LiveSessionListResponse:
    """Côté student : historique de ses sessions live, notes de
    l'examinateur incluses une fois la session terminée."""
    service = LiveSessionService(db)
    items, total = await service.list_for_student(current_user.id, limit=limit, offset=offset)
    return LiveSessionListResponse(items=await service.to_response_list(items), total=total)


@router.get("/launched", response_model=LiveSessionListResponse)
async def get_launched_live_sessions(
    current_user: CurrentUser,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> LiveSessionListResponse:
    """Côté examinateur : sessions qu'il/elle a lancées."""
    service = LiveSessionService(db)
    items, total = await service.list_for_examiner(current_user.id, limit=limit, offset=offset)
    return LiveSessionListResponse(items=await service.to_response_list(items), total=total)


@router.get("/{live_session_id}", response_model=LiveSessionResponse)
async def get_live_session(
    live_session_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> LiveSessionResponse:
    """Accessible au candidat ou à l'examinateur concerné par cette session.
    Déclarée en DERNIER parmi les routes GET : FastAPI matche dans l'ordre
    de déclaration, donc un chemin dynamique comme celui-ci doit toujours
    venir après les routes statiques ("/mine", "/launched"), sinon il les
    intercepterait en premier (live_session_id="mine" -> échec UUID)."""
    service = LiveSessionService(db)
    session = await service.get_or_404(live_session_id)
    if current_user.id not in (session.examiner_id, session.student_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette session.")
    return await service.to_response(session)


@router.get("/{live_session_id}/subject", response_model=SubjectContentResponse)
async def get_live_session_subject(
    live_session_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> SubjectContentResponse:
    """Contenu du sujet Sprechen (instructions/thèmes/points par Teil) —
    ce qui manquait jusqu'ici : le candidat et l'examinateur ne recevaient
    aucune information sur le sujet réellement sélectionné pour la session."""
    service = LiveSessionService(db)
    session = await service.get_or_404(live_session_id)
    if current_user.id not in (session.examiner_id, session.student_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette session.")

    content = await service.get_subject_content(live_session_id)
    return SubjectContentResponse.model_validate(content)