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

class TaskSchema(BaseModel):
    teil: int                                    # 1, 2 ou 3
    scenario: str                                # Consigne principale
    prompts: list[str] = Field(default_factory=list)   # Points à traiter
    topic: str = ""                              # Goethe/ÖSD B2 Teil 1
    context_ad: str = ""                         # Telc B2 / ÖSD B2
    opinion_quote: str = ""                      # Goethe B1 Teil 2
    word_count_min: int = 100
    word_count_max: int = 200


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


class SimulatorCorrectResponse(BaseModel):
    """Réutilise exactement le même format que CorrectionResponse."""
    subject_id: uuid.UUID
    provider: str
    level: str
    overall_score: int
    max_score: int
    passed: bool
    score_percentage: float
    aufgabe_score: int
    kohaesion_score: int
    wortschatz_score: int
    grammatik_score: int
    criteria_feedbacks: dict
    task_feedbacks: dict
    corrections_list: list[dict]
    suggestions: list[str]
    appreciation: str
    
    
class SimulatorResultResponse(BaseModel):
    id:               uuid.UUID
    subject_id:       uuid.UUID
    subject_title:    str | None = None
    provider:         str
    level:            str
    overall_score:    int
    max_score:        int
    passed:           bool
    score_percentage: float
    result_data:      dict
    created_at:       datetime
    model_config = {"from_attributes": True}