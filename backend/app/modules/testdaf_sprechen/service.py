"""
testdaf_sprechen.service
===========================
Session Sprechen TestDaF en mode enregistré (sans IA en direct).

Déroulé :
  1. start()      : charge le sujet, débite les crédits (fait par le
                    router), génère/rappelle les voix de l'interlocuteur,
                    renvoie les 7 tâches à jouer côté navigateur.
  2. add_recording() : reçoit l'enregistrement d'une tâche et lance sa
                    transcription Gemini en arrière-plan. Une session qui
                    plante à la tâche 5 ne perd pas les 4 premières.
  3. finish()     : attend les transcriptions, retente une fois celles qui
                    ont échoué, corrige avec Claude, enregistre le résultat
                    dans la même table que les autres oraux (il apparaît
                    dans "Mes résultats") et renvoie le même format de
                    résultat que sprechen_agent.

Stockage en mémoire du process, comme sprechen_agent (V1).
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sprechen_agent import repository
from app.modules.sprechen_agent import schemas as sprechen_schemas
from app.modules.sprechen_agent.service import SprechenAgentService
from app.modules.sprechen_agent.session_state import CriterionScore, TeilGrading

from . import grading, transcription, tts
from .schemas import TestDafTaskOut

TESTDAF_FORMAT_TYPE = "oral_testdaf"
SESSION_TTL = timedelta(hours=3)
FINISH_TRANSCRIPTION_TIMEOUT_SECONDS = 90.0
LIVE_PROVIDER_LABEL = "recorded"


class TestDafSessionError(Exception):
    pass


@dataclass
class _Recording:
    audio: bytes
    mime_type: str | None
    transcript: str | None = None
    task: asyncio.Task | None = None


@dataclass
class TestDafSession:
    session_id: UUID
    student_id: UUID
    subject_id: UUID
    provider: str
    level: str
    tasks: list[dict[str, Any]]  # contenu complet (Lösungshinweise compris), jamais renvoyé tel quel
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    recordings: dict[int, _Recording] = field(default_factory=dict)
    finished: bool = False
    # Crédits débités au démarrage (faux pour un admin) : rendus si la
    # session n'arrive pas jusqu'à la correction
    credits_charged: bool = False


_STORE: dict[UUID, TestDafSession] = {}
_LOCK = asyncio.Lock()


async def _purge_old_sessions() -> None:
    limit = datetime.now(timezone.utc) - SESSION_TTL
    async with _LOCK:
        for sid in [sid for sid, s in _STORE.items() if s.started_at < limit]:
            _STORE.pop(sid, None)


async def get_session(session_id: UUID, student_id: UUID) -> TestDafSession:
    async with _LOCK:
        session = _STORE.get(session_id)
    if session is None or session.student_id != student_id:
        raise TestDafSessionError("Session introuvable.")
    return session


async def forget_session(session_id: UUID) -> None:
    async with _LOCK:
        _STORE.pop(session_id, None)


def extract_tasks(subject_raw: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = [t for t in subject_raw.get("teile", []) if t.get("format_type") == TESTDAF_FORMAT_TYPE]
    return sorted(tasks, key=lambda t: t.get("teil_number", 0))


async def create_session(
    *, student_id: UUID, subject_id: UUID, subject_raw: dict[str, Any], provider: str, level: str
) -> TestDafSession:
    await _purge_old_sessions()
    tasks = extract_tasks(subject_raw)
    if not tasks:
        raise TestDafSessionError("Ce sujet n'a pas de tâches Sprechen TestDaF.")

    session = TestDafSession(
        session_id=uuid4(),
        student_id=student_id,
        subject_id=subject_id,
        provider=provider,
        level=level,
        tasks=tasks,
    )
    async with _LOCK:
        _STORE[session.session_id] = session
    return session


async def build_public_tasks(session: TestDafSession, audio_url_for) -> list[TestDafTaskOut]:
    """audio_url_for(filename) -> URL absolue de la route audio."""
    out: list[TestDafTaskOut] = []
    for task in session.tasks:
        statement_files, question_file = await tts.build_task_audio(task.get("audio_prompt"))
        lines = tts.parse_audio_prompt(task.get("audio_prompt"))
        out.append(
            TestDafTaskOut(
                teil_number=task["teil_number"],
                name=task.get("name", ""),
                situation=task.get("situation"),
                instructions=task.get("instructions"),
                prep_seconds=int(task.get("prep_seconds") or 0),
                speak_seconds=int(task.get("speak_seconds") or 0),
                max_score=float(task.get("max_score") or 0),
                stimulus_text=task.get("stimulus_text"),
                stimulus_hidden_after_seconds=task.get("stimulus_hidden_after_seconds"),
                grafik=task.get("grafik"),
                grafik_seconds=task.get("grafik_seconds"),
                gliederung=task.get("gliederung"),
                gliederung_title=task.get("gliederung_title"),
                listen_seconds=task.get("listen_seconds"),
                statement_audio_urls=[audio_url_for(f) for f in statement_files],
                question_audio_url=audio_url_for(question_file) if question_file else None,
                interlocutor=lines[-1].speaker if lines else None,
            )
        )
    return out


async def _transcribe_into(recording: _Recording, gemini_api_key: str) -> None:
    try:
        recording.transcript = await transcription.transcribe(
            recording.audio, recording.mime_type, api_key=gemini_api_key
        )
    except Exception:  # noqa: BLE001 : retenté une fois dans finish()
        recording.transcript = None


async def add_recording(
    session: TestDafSession,
    teil_number: int,
    audio: bytes,
    mime_type: str | None,
    *,
    gemini_api_key: str,
) -> None:
    if session.finished:
        raise TestDafSessionError("Session déjà terminée.")
    if teil_number not in {t["teil_number"] for t in session.tasks}:
        raise TestDafSessionError("Tâche inconnue.")

    previous = session.recordings.get(teil_number)
    if previous and previous.task and not previous.task.done():
        previous.task.cancel()

    recording = _Recording(audio=audio, mime_type=mime_type)
    recording.task = asyncio.create_task(_transcribe_into(recording, gemini_api_key))
    session.recordings[teil_number] = recording


async def _collect_transcripts(session: TestDafSession, gemini_api_key: str) -> dict[int, str]:
    pending = [r.task for r in session.recordings.values() if r.task and not r.task.done()]
    if pending:
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True),
                                   timeout=FINISH_TRANSCRIPTION_TIMEOUT_SECONDS)

    # Une seconde chance pour les transcriptions échouées
    retry = [r for r in session.recordings.values() if r.transcript is None and r.audio]
    if retry:
        await asyncio.gather(*(_transcribe_into(r, gemini_api_key) for r in retry))

    return {n: (r.transcript or "[Transkription fehlgeschlagen]") for n, r in session.recordings.items()}


async def finish(
    db: AsyncSession,
    session: TestDafSession,
    *,
    gemini_api_key: str,
    anthropic_api_key: str,
) -> sprechen_schemas.GradingResponse:
    if session.finished:
        raise TestDafSessionError("Session déjà terminée.")
    session.finished = True

    transcripts = await _collect_transcripts(session, gemini_api_key)
    result = await grading.call_claude_grading(
        session.tasks, transcripts, anthropic_api_key=anthropic_api_key
    )
    passed = result.level_estimate != "unter TDN 3"

    teile = [
        TeilGrading(
            teil_number=g.teil_number,
            criteria=[
                CriterionScore(
                    criterion_name=grading.CRITERION_NAME,
                    score=g.score,
                    max_score=g.max_score,
                    issue=g.issue,
                    model_phrase=g.model_phrase,
                    tip=g.tip,
                )
            ],
            teil_score=g.score,
            teil_max_score=g.max_score,
        )
        for g in result.tasks
    ]
    transcript_rows = [
        {
            "teil_number": n,
            "step_order": 1,
            "speaker": "student",
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for n, text in sorted(transcripts.items())
    ]

    agent_service = SprechenAgentService(db)
    previous_percent = await agent_service._get_previous_attempt_score(
        student_id=session.student_id, subject_id=session.subject_id
    )

    await repository.create_session_result(
        db,
        student_id=session.student_id,
        subject_id=session.subject_id,
        provider=session.provider,
        level=session.level,
        teile_breakdown=[t.model_dump(mode="json") for t in teile],
        total_score=result.total_score,
        total_max_score=result.total_max_score,
        passed=passed,
        level_estimate=result.level_estimate,
        strengths=result.strengths,
        improvement_areas=result.improvement_areas,
        transcript=transcript_rows,
        live_provider_used=LIVE_PROVIDER_LABEL,
        started_at=session.started_at,
    )
    await db.commit()
    await forget_session(session.session_id)

    names = {g.teil_number: g.name for g in result.tasks}
    percent = (result.total_score / result.total_max_score * 100) if result.total_max_score else 0.0
    return sprechen_schemas.GradingResponse(
        session_id=session.session_id,
        provider=session.provider,
        level=session.level,
        teile=[
            sprechen_schemas.TeilGradingOut(
                teil_number=t.teil_number,
                teil_name=names.get(t.teil_number, f"Aufgabe {t.teil_number}"),
                criteria=[
                    sprechen_schemas.CriterionScoreOut(**c.model_dump()) for c in t.criteria
                ],
                teil_score=t.teil_score,
                teil_max_score=t.teil_max_score,
            )
            for t in teile
        ],
        total_score=result.total_score,
        total_max_score=result.total_max_score,
        passed=passed,
        level_estimate=result.level_estimate,
        strengths=result.strengths,
        improvement_areas=result.improvement_areas,
        graded_at=datetime.now(timezone.utc),
        previous_score_percent=previous_percent,
        score_delta_percent=(percent - previous_percent) if previous_percent is not None else None,
    )


def cancel_pending(session: TestDafSession) -> None:
    for r in session.recordings.values():
        if r.task and not r.task.done():
            r.task.cancel()