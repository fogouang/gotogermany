"""
app/modules/exam_access/schemas.py

ExamAccess est rarement exposé seul — il est surtout
utilisé en interne pour vérifier les droits d'accès.
On expose uniquement ce dont le frontend a besoin :
  - savoir si l'user a accès à un exam donné
  - lister les examens accessibles de l'user
"""
import uuid
from datetime import datetime
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────

class ExamAccessResponse(BaseSchema):
    """Accès à un exam — retourné après paiement ou inscription."""
    id: uuid.UUID
    exam_id: uuid.UUID
    access_type: str            # "free" | "paid"
    granted_at: datetime
    expires_at: datetime | None
    is_active: bool


class ExamAccessWithExamResponse(ExamAccessResponse):
    """
    Accès enrichi avec infos de l'exam — pour la liste
    des examens accessibles de l'user (GET /users/me/exams).
    """
    exam_name: str
    exam_slug: str
    exam_provider: str
    cefr_code: str


class UserExamsResponse(BaseSchema):
    """
    Tous les examens d'un user avec leur statut d'accès.
    Retourné par GET /users/me/exams.
    """
    free_exams: list[ExamAccessWithExamResponse] = []
    paid_exams: list[ExamAccessWithExamResponse] = []
    total: int


class AccessCheckResponse(BaseSchema):
    """
    Vérification rapide d'accès avant démarrage d'une session.
    Retourné par GET /exams/{exam_id}/access.
    """
    exam_id: uuid.UUID
    has_access: bool
    access_type: str | None     # "free" | "paid" | None si pas d'accès
    expires_at: datetime | None
    reason: str | None          # "Accès gratuit", "Accès payant actif", "Accès requis"