"""
app/modules/corrections/schemas.py

Schémas Pydantic pour l'API de correction IA.

Le frontend envoie uniquement l'exam_session_id.
Le service récupère tout le reste depuis la DB (textes, instructions, provider, level).
"""
from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, computed_field


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

class TaskFeedback(BaseModel):
    """Feedback pour une tâche individuelle."""
    corrected_text: str
    main_strengths: list[str] = Field(default_factory=list)
    main_weaknesses: list[str] = Field(default_factory=list)


class CorrectionError(BaseModel):
    """Une erreur identifiée avec sa correction."""
    error: str
    correction: str
    explanation: str
    task: str = "1"   # Numéro de la tâche concernée


class CriteriaScores(BaseModel):
    """Scores par critère d'évaluation."""
    aufgabe_score: int
    aufgabe_feedback: str
    kohaesion_score: int
    kohaesion_feedback: str
    wortschatz_score: int
    wortschatz_feedback: str
    grammatik_score: int
    grammatik_feedback: str


# ─────────────────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────────────────

class CorrectionResponse(BaseModel):
    """Réponse complète retournée au frontend."""

    id: uuid.UUID
    session_id: uuid.UUID

    # Contexte examen
    provider: str
    level: str

    # Scores
    overall_score: int
    max_score: int
    passed: bool
    score_percentage: float

    # Scores par critère
    aufgabe_score: int
    kohaesion_score: int
    wortschatz_score: int
    grammatik_score: int

    # Feedbacks
    criteria_feedbacks: dict        # {"aufgabe_feedback": "...", ...}
    task_feedbacks: dict            # {"task1": TaskFeedback, ...}
    corrections_list: list[dict]    # [CorrectionError, ...]
    suggestions: list[str]
    appreciation: str

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
    max_score: int                      # 45 | 90 | 100
    tasks: list[TaskPayload]