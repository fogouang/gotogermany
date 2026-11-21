"""
app/modules/testdaf_sprechen/router.py
=========================================
Sprechen TestDaF en mode enregistré (fidèle au TestDaF digital) :

  POST /sessions                               démarre (2 crédits), renvoie les 7 tâches
  POST /sessions/{id}/tasks/{n}/recording      enregistrement d'une tâche (multipart "file")
  POST /sessions/{id}/finish                   transcription + correction, résultat final
  POST /sessions/{id}/abandon                  abandon, crédits rendus
  GET  /audio/{filename}                       voix de l'interlocuteur (mp3 en cache)

La route audio est publique : un <audio src> ne peut pas envoyer de
jeton, et les noms de fichiers sont des empreintes impossibles à deviner.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.modules.auth.dependencies import CurrentUser
from app.modules.sprechen_agent import schemas as sprechen_schemas
from app.modules.sprechen_agent.router import (
    SPRECHEN_CREDIT_COST,
    _charge_credits,
    _credits_exempt,
    _refund_credits,
    _SubjectUnavailable,
    load_subject_data,
)
from app.shared.database.session import get_db

from . import service, tts
from .schemas import (
    RecordingReceivedResponse,
    StartTestDafSessionRequest,
    StartTestDafSessionResponse,
)

router = APIRouter()

MAX_RECORDING_BYTES = 15 * 1024 * 1024  # largement assez pour 2 min 30 en opus


def _not_found(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/sessions", response_model=StartTestDafSessionResponse)
async def start_testdaf_session(
    body: StartTestDafSessionRequest,
    request: Request,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> StartTestDafSessionResponse:
    try:
        subject_raw, provider, level = await load_subject_data(db, body.subject_id, current_user)
    except _SubjectUnavailable as exc:
        raise _not_found(exc)

    if provider.lower() != "testdaf":
        raise HTTPException(status_code=400, detail="Ce sujet n'est pas un sujet TestDaF.")

    try:
        session = await service.create_session(
            student_id=current_user.id,
            subject_id=body.subject_id,
            subject_raw=subject_raw,
            provider=provider,
            level=level,
        )
    except service.TestDafSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not _credits_exempt(current_user):
        if not await _charge_credits(db, current_user.id):
            await service.forget_session(session.session_id)
            raise HTTPException(status_code=402, detail="Crédits insuffisants.")
        session.credits_charged = True

    try:
        tasks = await service.build_public_tasks(
            session,
            lambda filename: str(request.url_for("get_testdaf_audio", filename=filename)),
        )
    except Exception as exc:  # noqa: BLE001 : génération audio impossible, on rend les crédits
        if session.credits_charged:
            await _refund_credits(db, current_user.id)
        await service.forget_session(session.session_id)
        raise HTTPException(status_code=502, detail=f"Génération audio impossible : {exc}")

    total_seconds = sum(
        t.prep_seconds + t.speak_seconds + (t.listen_seconds or 0) + (t.grafik_seconds or 0)
        for t in tasks
    )
    return StartTestDafSessionResponse(
        session_id=session.session_id,
        provider=provider,
        level=level,
        total_minutes=max(1, round(total_seconds / 60)),
        tasks=tasks,
    )


@router.post(
    "/sessions/{session_id}/tasks/{teil_number}/recording",
    response_model=RecordingReceivedResponse,
)
async def upload_testdaf_recording(
    session_id: UUID,
    teil_number: int,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> RecordingReceivedResponse:
    try:
        session = await service.get_session(session_id, current_user.id)
    except service.TestDafSessionError as exc:
        raise _not_found(exc)

    audio = await file.read()
    if len(audio) > MAX_RECORDING_BYTES:
        raise HTTPException(status_code=413, detail="Enregistrement trop volumineux.")

    try:
        await service.add_recording(
            session, teil_number, audio, file.content_type, gemini_api_key=settings.GEMINI_API_KEY
        )
    except service.TestDafSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RecordingReceivedResponse(teil_number=teil_number)


@router.post("/sessions/{session_id}/finish", response_model=sprechen_schemas.GradingResponse)
async def finish_testdaf_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> sprechen_schemas.GradingResponse:
    try:
        session = await service.get_session(session_id, current_user.id)
    except service.TestDafSessionError as exc:
        raise _not_found(exc)

    try:
        return await service.finish(
            db,
            session,
            gemini_api_key=settings.GEMINI_API_KEY,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
        )
    except service.TestDafSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # noqa: BLE001 : correction impossible, crédits rendus
        if session.credits_charged:
            await _refund_credits(db, current_user.id)
            session.credits_charged = False
        await service.forget_session(session.session_id)
        raise HTTPException(status_code=502, detail=f"Correction impossible : {exc}")


@router.post("/sessions/{session_id}/abandon", status_code=status.HTTP_204_NO_CONTENT)
async def abandon_testdaf_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        session = await service.get_session(session_id, current_user.id)
    except service.TestDafSessionError:
        return  # déjà terminée ou expirée : rien à faire
    if session.finished:
        return
    service.cancel_pending(session)
    if session.credits_charged:
        await _refund_credits(db, current_user.id)
        session.credits_charged = False
    await service.forget_session(session.session_id)


@router.get("/audio/{filename}", name="get_testdaf_audio")
async def get_testdaf_audio(filename: str) -> FileResponse:
    path = tts.cache_path(filename)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail="Audio introuvable.")
    return FileResponse(path, media_type="audio/mpeg")