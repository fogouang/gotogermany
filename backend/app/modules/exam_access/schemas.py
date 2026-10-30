"""
app/modules/exam_access/schemas.py

ExamAccess est rarement exposé seul : il sert surtout en interne pour
vérifier les droits. On expose ce dont le frontend a besoin :
  - savoir si l'user a accès à un niveau donné
  - lister les niveaux accessibles de l'user
  - les 3 premiers sujets sont toujours libres (logique backend)
"""
import uuid
from datetime import datetime
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────

class ExamAccessResponse(BaseSchema):
    """Accès à un niveau, retourné après grant admin ou paiement."""
    id: uuid.UUID
    level_id: uuid.UUID | None      # niveau du catalogue des examens
    sd_level: str | None = None     # ou niveau Start Deutsch ("A1", "A2")
    access_type: str                # "paid" | "admin"
    granted_at: datetime
    expires_at: datetime | None
    is_active: bool


class ExamAccessWithLevelResponse(ExamAccessResponse):
    """
    Accès enrichi avec infos du niveau et de l'examen parent.
    Pour la liste des niveaux accessibles de l'user.
    """
    cefr_code: str              # "B1", "B2", "A1"...
    exam_name: str              # "Goethe-ÖSD Zertifikat B1", "Start Deutsch A1"
    exam_provider: str          # "Goethe", "TELC", "start_deutsch"...


class UserLevelsResponse(BaseSchema):
    """
    Tous les niveaux payants accessibles d'un user.
    Les 3 premiers sujets de chaque niveau sont libres par défaut
    et ne figurent pas ici : ils sont gérés côté backend.
    """
    paid_levels: list[ExamAccessWithLevelResponse] = []
    total: int


class AccessCheckResponse(BaseSchema):
    """
    Vérification rapide d'accès à un niveau.
    Retourné par GET /exam-access/check/{level_id}.
    """
    level_id: uuid.UUID
    has_access: bool
    access_type: str | None     # "paid" | None si pas d'accès
    expires_at: datetime | None
    reason: str | None          # "Accès payant actif" | "Accès requis"