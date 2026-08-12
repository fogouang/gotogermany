"""
app/modules/start_deutsch/schemas.py

Schémas Pydantic pour le module Start Deutsch (A1/A2).
Pydantic v2 (model_config = ConfigDict(from_attributes=True)).

Toutes les classes sont préfixées "StartDeutsch" — pas par style, mais
par nécessité : openapi-typescript-codegen désambiguïse deux classes de
même nom entre modules en les préfixant par le chemin du module
(ex. app__modules__exam_sessions__schemas__SessionResultResponse), ce qui
fait disparaître l'export "plat" que le code existant utilisait. Le
préfixe systématique évite ce genre de collision, y compris pour de futurs
schémas qui n'entrent pas encore en conflit aujourd'hui.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Catalogue : lecture ────────────────────────────────────────────

class StartDeutschTeilPublic(BaseModel):
    """Un Teil tel que vu par l'étudiant — pas de correct_answer dans les questions imbriquées."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    teil_number: int
    format_type: str
    instructions: str | None
    audio_file: str | None
    max_score: int
    shared_content: dict | None = None
    questions: list["StartDeutschQuestionPublic"] = Field(default_factory=list)


class StartDeutschQuestionPublic(BaseModel):
    """Une question sans son correct_answer — c'est ce que l'étudiant reçoit pendant la session."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_number: int
    content: dict
    points: float
    image_file: str | None


class StartDeutschQuestionWithAnswer(StartDeutschQuestionPublic):
    """Variante admin/correction — inclut la réponse correcte."""

    correct_answer: dict | None


class StartDeutschModulePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    order: int
    max_score: int
    teile: list[StartDeutschTeilPublic] = Field(default_factory=list)


class StartDeutschSubjectSummary(BaseModel):
    """Version légère pour les listes de catalogue (pas de modules imbriqués)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    level: str
    subject_number: int
    title: str
    description: str | None
    is_active: bool


class StartDeutschSubjectDetail(StartDeutschSubjectSummary):
    """Version complète avec l'arbre Module → Teil → Question, pour démarrer une session."""

    modules: list[StartDeutschModulePublic] = Field(default_factory=list)


# ── Sessions ────────────────────────────────────────────────────────

class StartDeutschSessionCreateRequest(BaseModel):
    subject_id: uuid.UUID


class StartDeutschSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    subject_id: uuid.UUID
    status: str
    score: float | None
    passed: bool | None
    started_at: datetime
    submitted_at: datetime | None


class StartDeutschSessionListItem(BaseModel):
    """Pour la page liste des tentatives (équivalent my-results)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    status: str
    score: float | None
    passed: bool | None
    started_at: datetime
    submitted_at: datetime | None


# ── Soumission de réponses ─────────────────────────────────────────

class StartDeutschAnswerSubmit(BaseModel):
    question_id: uuid.UUID
    user_answer: dict


class StartDeutschSessionSubmitRequest(BaseModel):
    answers: list[StartDeutschAnswerSubmit]


class StartDeutschAnswerResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: uuid.UUID
    question_number: int
    user_answer: dict
    correct_answer: dict | None
    is_correct: bool | None
    score_obtained: float


class StartDeutschTeilResult(BaseModel):
    teil_id: uuid.UUID
    teil_number: int
    format_type: str
    max_score: int
    score_obtained: float
    answers: list[StartDeutschAnswerResult] = Field(default_factory=list)


class StartDeutschModuleResult(BaseModel):
    module_id: uuid.UUID
    slug: str
    max_score: int
    score_obtained: float
    is_corrected: bool
    teile: list[StartDeutschTeilResult] = Field(default_factory=list)


class StartDeutschSessionResultResponse(BaseModel):
    """Résultat complet d'une session — pensé pour alimenter une page de résultat
    du même esprit que celle déjà en place pour B1/B2 (score par Teil/module,
    seuil de réussite, réponses détaillées)."""

    session_id: uuid.UUID
    subject_id: uuid.UUID
    subject_title: str
    level: str
    status: str
    score: float | None
    total_pass_score: float
    passed: bool | None
    started_at: datetime
    submitted_at: datetime | None
    modules: list[StartDeutschModuleResult] = Field(default_factory=list)


# ── Correction Schreiben (IA) ───────────────────────────────────────

class StartDeutschCriterionScore(BaseModel):
    grade: str  # "A" à "E", cf. barème officiel
    points: float
    label: str | None = None
    feedback: str | None = None


class StartDeutschSchreibenCorrectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    teil_id: uuid.UUID
    submitted_text: str
    criteria_scores: dict[str, StartDeutschCriterionScore]
    overall_score: float
    max_score: float
    passed: bool
    feedback: str | None
    created_at: datetime


class StartDeutschSchreibenCorrectionRequest(BaseModel):
    teil_id: uuid.UUID
    submitted_text: str