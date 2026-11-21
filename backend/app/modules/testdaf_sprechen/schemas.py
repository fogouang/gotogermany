"""
testdaf_sprechen.schemas
===========================
Contrat REST du Sprechen TestDaF en mode enregistré.

Ce que l'élève reçoit d'une tâche : tout ce qui s'affiche à l'examen
(situation, consigne, texte, graphique, plan) et les URL audio de
l'interlocuteur. JAMAIS les Lösungshinweise, ni le texte de l'audio
(à l'examen on l'entend, on ne le lit pas).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class StartTestDafSessionRequest(BaseModel):
    subject_id: UUID


class TestDafTaskOut(BaseModel):
    teil_number: int
    name: str
    situation: str | None = None
    instructions: str | None = None
    prep_seconds: int
    speak_seconds: int
    max_score: float
    # Supports affichés
    stimulus_text: str | None = None
    stimulus_hidden_after_seconds: int | None = None
    grafik: dict[str, Any] | None = None
    grafik_seconds: int | None = None
    gliederung: list[str] | None = None
    gliederung_title: str | None = None
    # Audio : déclaration (avant la préparation) puis question (avant l'enregistrement)
    listen_seconds: int | None = None
    statement_audio_urls: list[str] = []
    question_audio_url: str | None = None
    interlocutor: str | None = None


class StartTestDafSessionResponse(BaseModel):
    session_id: UUID
    provider: str
    level: str
    total_minutes: int
    tasks: list[TestDafTaskOut]


class RecordingReceivedResponse(BaseModel):
    teil_number: int
    received: bool = True