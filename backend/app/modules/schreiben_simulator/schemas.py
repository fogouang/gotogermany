"""
app/modules/schreiben_simulator/schemas.py
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────
# Sous-schéma : une tâche dans un sujet
# ─────────────────────────────────────────────────────────

class ThemeSchema(BaseModel):
    titel: str = ""
    stimulus: str = ""
    prompts: list[str] = Field(default_factory=list)


class OpinionVariantSchema(BaseModel):
    thema: str = ""
    aussagen: list[str] = Field(default_factory=list)


class StimulusEmailSchema(BaseModel):
    sender: str = ""
    subject: str = ""
    body: str = ""


class InfoComparisonSchema(BaseModel):
    anbieter: str = ""
    situation: str = ""
    versprechen: list[str] = Field(default_factory=list)
    probleme: list[str] = Field(default_factory=list)
    kontakt: str = ""


class TaskSchema(BaseModel):
    teil: int
    scenario: str = ""
    prompts: list[str] = Field(default_factory=list)
    topic: str = ""
    context_ad: str = ""
    opinion_quote: str = ""
    word_count_min: int = 100
    word_count_max: int = 200
    # Champs riches, optionnels — présents seulement pour les sujets
    # venant de la hiérarchie unifiée (Question.content), absents pour
    # les anciens sujets schreiben_subjects saisis à la main.
    stimulus: str | dict | None = None
    stimulus_author: str = ""
    themes: dict[str, ThemeSchema] | None = None
    opinion_variants: dict[str, OpinionVariantSchema] | None = None
    stimulus_email: StimulusEmailSchema | None = None
    info_comparison: InfoComparisonSchema | None = None
    leitpunkte: list[str] = Field(default_factory=list)
    word_count_target: int | None = None
    register: str = ""
    recipient: str = ""


# ─────────────────────────────────────────────────────────
# CRUD Admin
# ─────────────────────────────────────────────────────────

class SchreibenSubjectCreate(BaseModel):
    provider: Literal["telc", "goethe", "osd"]
    level: Literal["b1", "b2"]
    title: str
    description: str | None = None
    tasks: list[TaskSchema]
    display_order: int = 0
    is_active: bool = True


class SchreibenSubjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    tasks: list[TaskSchema] | None = None
    display_order: int | None = None
    is_active: bool | None = None


class SchreibenSubjectResponse(BaseModel):
    id: uuid.UUID
    provider: str
    level: str
    title: str
    description: str | None
    tasks: list[dict]
    display_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
# Simulateur utilisateur
# ─────────────────────────────────────────────────────────

class SimulatorCorrectRequest(BaseModel):
    """
    Le frontend envoie le sujet + les textes rédigés par le candidat.
    task_texts est une liste ordonnée : [texte_teil1, texte_teil2, ...]
    """
    subject_id: uuid.UUID
    task_texts: list[str]    # 1, 2 ou 3 textes selon le sujet


class CriterionScore(BaseModel):
    """Un critère de notation générique — même contrat que corrections/schemas.py."""
    key: str
    label: str
    score: float
    max_score: float
    feedback: str = ""


class SubCriterionScore(BaseModel):
    """Composante fine d'un critère, propre à certains barèmes (ex. ÖSD B2 : a/k/t/l/f par tâche)."""
    key: str
    label: str
    score: float
    max_score: float


class TaskFeedback(BaseModel):
    """Feedback pour une tâche individuelle — même contrat que corrections/schemas.py."""
    key: str
    label: str
    corrected_text: str
    main_strengths: list[str] = Field(default_factory=list)
    main_weaknesses: list[str] = Field(default_factory=list)
    score: float | None = None
    max_score: float | None = None
    sub_criteria: list[SubCriterionScore] | None = None


class SimulatorCorrectResponse(BaseModel):
    """
    Réutilise exactement le même contrat que corrections.schemas.CorrectionResponse
    (criteria/tasks génériques, produits par response_normalizer), moins id/session_id
    puisqu'ici il n'y a pas de session — remplacés par subject_id.
    """
    subject_id: uuid.UUID
    provider: str
    level: str
    overall_score: float
    max_score: float
    passed: bool
    score_percentage: float
    appreciation: str

    # ÖSD B2 uniquement : vrai plancher officiel, distinct de `passed`
    # (repère interne à 60%, cf. osd_b2_prompt.py). None pour les autres examens.
    floor_reached: bool | None = None

    criteria: list[CriterionScore]
    tasks: list[TaskFeedback]

    corrections_list: list[dict]
    suggestions: list[str]


class SimulatorResultResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    subject_title: str | None = None
    provider: str
    level: str
    overall_score: float
    max_score: float
    passed: bool
    score_percentage: float
    # Contient désormais directement la forme normalisée (criteria/tasks/...),
    # produite par response_normalizer au moment de la correction et persistée
    # telle quelle — pas de retraitement nécessaire à la lecture.
    result_data: dict
    created_at: datetime
    model_config = {"from_attributes": True}