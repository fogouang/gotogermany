"""
app/modules/questions/schemas.py

Les questions ont un contenu JSONB flexible selon leur type.
On expose deux niveaux de response :
  - QuestionResponse        → contenu sans correct_answer (vue étudiant)
  - QuestionAdminResponse   → contenu + correct_answer (vue admin / import)
"""
import uuid
from typing import Any
from pydantic import Field
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Requests
# ─────────────────────────────────────────────

class QuestionCreateRequest(BaseSchema):
    question_number: int = Field(gt=0)
    question_type: str = Field(max_length=50)
    content: dict[str, Any]
    correct_answer: dict[str, Any]
    points: int = Field(default=1, gt=0)
    audio_file: str | None = Field(default=None, max_length=255)


class QuestionUpdateRequest(BaseSchema):
    content: dict[str, Any] | None = None
    correct_answer: dict[str, Any] | None = None
    points: int | None = Field(default=None, gt=0)
    audio_file: str | None = None


class BulkQuestionCreateRequest(BaseSchema):
    """Import en masse depuis le JSON de l'examen."""
    questions: list[QuestionCreateRequest]


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────

class QuestionResponse(BaseSchema):
    """
    Vue étudiant — correct_answer exclu.
    Le frontend affiche le contenu et collecte la réponse.
    """
    id: uuid.UUID
    teil_id: uuid.UUID
    question_number: int
    question_type: str
    content: dict[str, Any]
    points: int
    audio_file: str | None


class QuestionAdminResponse(QuestionResponse):
    """
    Vue admin — inclut correct_answer pour vérification et import.
    """
    correct_answer: dict[str, Any]


class TeilWithQuestionsResponse(BaseSchema):
    """
    Teil complet avec ses questions — utilisé lors du démarrage
    d'une session pour charger le contenu d'un module.
    """
    id: uuid.UUID
    teil_number: int
    format_type: str
    instructions: str | None
    max_score: int
    time_minutes: int | None
    config: dict[str, Any] | None   # stimulus_text, anzeigen, speakers...
    questions: list[QuestionResponse] = []


class ModuleSessionResponse(BaseSchema):
    """
    Module complet pour une session d'examen.
    Retourné au démarrage d'une session — contient tout le contenu
    nécessaire pour afficher le module sans appels supplémentaires.
    """
    id: uuid.UUID
    slug: str
    name: str
    time_limit_minutes: int
    max_score: int
    display_order: int
    teile: list[TeilWithQuestionsResponse] = []