"""
app/modules/corrections/schemas.py

Schémas Pydantic pour l'API de correction IA.

Le frontend envoie uniquement l'exam_session_id.
Le service récupère tout le reste depuis la DB (textes, instructions, provider, level).

⚠️ Changement structurel : les anciens champs plats et fixes
(aufgabe_score/kohaesion_score/wortschatz_score/grammatik_score, CriteriaScores,
task_feedbacks en dict) sont remplacés par des listes génériques `criteria` et
`tasks`, produites par response_normalizer.normalize_correction_result().
Nécessaire car les 5 barèmes (Goethe B2, Goethe/ÖSD B1, telc B1, telc B2, ÖSD B2)
n'ont plus le même nombre ni les mêmes noms de critères — voir response_normalizer.py.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────
# REQUEST
# ─────────────────────────────────────────────────────────

class CorrectionRequest(BaseModel):
    """
    Le frontend envoie uniquement l'ID de session.
    Tout le reste (textes, provider, level, instructions) est récupéré en DB.
    """
    exam_session_id: uuid.UUID


# ─────────────────────────────────────────────────────────
# SOUS-SCHEMAS pour la réponse
# ─────────────────────────────────────────────────────────

class CriterionScore(BaseModel):
    """Un critère de notation générique (Erfüllung, Leitpunkte, Aufgabe ÖSD B2 agrégé, etc.)."""
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
    """Feedback pour une tâche individuelle."""
    key: str                            # "task1", "task2", "task3"
    label: str                          # "Teil 1", "Teil 2"...
    corrected_text: str
    main_strengths: list[str] = Field(default_factory=list)
    main_weaknesses: list[str] = Field(default_factory=list)
    # Optionnels — remplis seulement pour les barèmes qui notent la tâche
    # individuellement (ex. ÖSD B2 : 15 pts/tâche avec détail A/K/T/L/F).
    # None pour les barèmes qui n'ont qu'un score global (Goethe, telc).
    score: float | None = None
    max_score: float | None = None
    sub_criteria: list[SubCriterionScore] | None = None


class CorrectionError(BaseModel):
    """Une erreur identifiée avec sa correction."""
    error: str
    correction: str
    explanation: str
    task: str = "1"   # Numéro de la tâche concernée


# ─────────────────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────────────────

class CorrectionResponse(BaseModel):
    """Réponse complète retournée au frontend — même forme pour tous les examens."""

    id: uuid.UUID
    session_id: uuid.UUID

    # Contexte examen
    provider: str
    level: str

    # Scores
    overall_score: float
    max_score: float
    passed: bool
    score_percentage: float
    appreciation: str

    # Champ optionnel — présent uniquement pour ÖSD B2, où `passed` (60% interne
    # à la plateforme) diffère du vrai plancher de certification ÖSD (>=10/30).
    floor_reached: bool | None = None

    # Critères et tâches — structure et nombre variables selon l'examen
    criteria: list[CriterionScore]
    tasks: list[TaskFeedback]

    corrections_list: list[CorrectionError]
    suggestions: list[str]

    # Meta
    ai_provider: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
# SCHEMA INTERNE — données assemblées avant appel IA
# ─────────────────────────────────────────────────────────

class TaskPayload(BaseModel):
    """
    Données d'une tâche extraites de la DB, prêtes pour le prompt.
    Usage interne au service uniquement.
    """
    teil_number: int
    text: str                           # Réponse du candidat
    instruction: str                    # Consigne (Question.content["scenario"])
    bullet_points: list[str] = Field(default_factory=list)
    opinion_quote: str = ""             # Goethe B1 Teil 2
    topic: str = ""                     # Goethe/ÖSD B2 Teil 1
    context_ad: str = ""                # Telc B2 / ÖSD B2


class CorrectionPayload(BaseModel):
    """
    Toutes les données nécessaires pour lancer une correction.
    Assemblé par le service avant d'appeler l'IA.
    """
    session_id: uuid.UUID
    user_id: uuid.UUID
    provider: str                       # telc | goethe | osd
    level: str                          # b1 | b2
    max_score: int                      # 45 | 90 | 100 | 30 (ÖSD B2)
    tasks: list[TaskPayload]