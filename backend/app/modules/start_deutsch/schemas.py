"""
app/modules/start_deutsch/schemas.py

Schémas Pydantic v2 du module Start Deutsch (A1, A2).

Toutes les classes commencent par "StartDeutsch" : openapi-typescript-codegen
renomme deux classes homonymes de modules différents avec le chemin complet
(app__modules__exam_sessions__schemas__...), ce qui casse les imports du front.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Catalogue : lecture ────────────────────────────────────────────

class StartDeutschTeilPublic(BaseModel):
    """Un Teil côté étudiant : les questions n'ont pas de correct_answer."""

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
    """Une question sans sa réponse, telle que l'étudiant la reçoit."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_number: int
    content: dict
    points: float
    image_file: str | None


class StartDeutschQuestionWithAnswer(StartDeutschQuestionPublic):
    """Admin et correction : avec la réponse attendue."""

    correct_answer: dict | None


class StartDeutschModulePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    order: int
    max_score: int
    teile: list[StartDeutschTeilPublic] = Field(default_factory=list)


class StartDeutschSubjectSummary(BaseModel):
    """Pour les listes : sans les modules."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    level: str
    subject_number: int
    title: str
    description: str | None
    is_active: bool
    is_private: bool = False
    # Catalogue élève : sujet fermé tant que le niveau n'est pas payé (cadenas)
    is_locked: bool = False


class StartDeutschSubjectUpdate(BaseModel):
    """Admin : activer, désactiver, rendre privé ou public."""

    is_active: bool | None = None
    is_private: bool | None = None


class StartDeutschSubjectDetail(StartDeutschSubjectSummary):
    """Avec l'arbre Module > Teil > Question, pour démarrer une session."""

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
    """Liste des tentatives de l'étudiant."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    subject_title: str = ""
    subject_number: int = 0
    level: str = ""
    status: str
    # Points bruts (Lesen, Hören, Schreiben) et pourcentage, sans le Sprechen
    score: float | None
    score_percent: float | None = None
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
    """Résultat d'une session : score par module et par Teil, seuil, réponses."""

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
    grade: str  # de "A" à "E", barème officiel
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