"""
app/modules/exam_access/schemas.py

ExamAccess est rarement exposé seul — il est surtout
utilisé en interne pour vérifier les droits d'accès.
On expose uniquement ce dont le frontend a besoin :
  - savoir si l'user a accès à un level donné
  - lister les levels accessibles de l'user
  - les 3 premiers sujets sont toujours libres (logique backend)
"""
import uuid
from datetime import datetime
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────

class ExamAccessResponse(BaseSchema):
    """Accès à un level — retourné après grant admin ou paiement."""
    id: uuid.UUID
    level_id: uuid.UUID         # remplace exam_id
    access_type: str            # "paid"
    granted_at: datetime
    expires_at: datetime | None
    is_active: bool


class ExamAccessWithLevelResponse(ExamAccessResponse):
    """
    Accès enrichi avec infos du level et de l'exam parent.
    Pour la liste des levels accessibles de l'user.
    """
    cefr_code: str              # "B1", "B2"...
    exam_name: str              # "Goethe-ÖSD Zertifikat B1"
    exam_provider: str          # "Goethe", "TELC"...


class UserLevelsResponse(BaseSchema):
    """
    Tous les levels payants accessibles d'un user.
    Les 3 premiers sujets de chaque level sont libres par défaut
    et ne figurent pas ici — ils sont gérés côté backend.
    """
    paid_levels: list[ExamAccessWithLevelResponse] = []
    total: int


class AccessCheckResponse(BaseSchema):
    """
    Vérification rapide d'accès à un level.
    Retourné par GET /exam-access/check/{level_id}.
    """
    level_id: uuid.UUID         # remplace exam_id
    has_access: bool
    access_type: str | None     # "paid" | None si pas d'accès
    expires_at: datetime | None
    reason: str | None          # "Accès payant actif" | "Accès requis"