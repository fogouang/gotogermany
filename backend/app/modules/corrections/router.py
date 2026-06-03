"""
app/modules/corrections/router.py

Endpoints pour la correction IA du module Schreiben.

POST   /corrections/                          → Lancer une correction
GET    /corrections/{correction_id}           → Récupérer par ID
GET    /corrections/session/{session_id}      → Récupérer par session
"""
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.corrections.schemas import CorrectionRequest, CorrectionResponse
from app.modules.corrections.service import CorrectionService

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Dépendance ───────────────────────────────────────────

def get_correction_service(db: AsyncSession = Depends(get_db)) -> CorrectionService:
    return CorrectionService(db)


# ── Endpoints ────────────────────────────────────────────

@router.post(
    "/",
    response_model=CorrectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Lancer la correction IA d'une session Schreiben",
    description=(
        "Lance la correction IA pour le module Schreiben d'une session d'examen. "
        "Si la correction existe déjà, elle est retournée sans rappeler l'IA."
    ),
)
async def create_correction(
    request: CorrectionRequest,
    current_user: User = Depends(get_current_user),
    service: CorrectionService = Depends(get_correction_service),
) -> CorrectionResponse:
    try:
        return await service.correct(request, current_user.id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé à cette session.",
        )
    except Exception as e:
        logger.error(f"Erreur correction session {request.exam_session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la correction IA : {str(e)}",
        )


@router.get(
    "/{correction_id}",
    response_model=CorrectionResponse,
    summary="Récupérer une correction par ID",
)
async def get_correction(
    correction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CorrectionService = Depends(get_correction_service),
) -> CorrectionResponse:
    try:
        return await service.get_by_id(correction_id, current_user.id)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correction introuvable.",
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé.",
        )


@router.get(
    "/session/{session_id}",
    response_model=CorrectionResponse | None,
    summary="Récupérer la correction d'une session",
    description=(
        "Retourne la correction existante pour cette session, "
        "ou null si elle n'a pas encore été corrigée."
    ),
)
async def get_correction_by_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CorrectionService = Depends(get_correction_service),
) -> CorrectionResponse | None:
    try:
        return await service.get_by_session(session_id, current_user.id)

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé.",
        )