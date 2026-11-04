"""
app/modules/security/router.py — admin uniquement

  GET  /security/summary                       → compteurs pour le badge du menu
  GET  /security/incidents?status=open         → liste des incidents
  GET  /security/incidents/{id}                → détail (compteurs + derniers accès)
  POST /security/incidents/{id}/resolve        → marquer traité
  GET  /security/blocks                        → élèves suspendus
  POST /security/users/{user_id}/unblock       → rétablir l'accès
  POST /security/users/{user_id}/ban           → désactiver le compte
  GET  /security/users/{user_id}/evidence      → dossier de preuves (JSON téléchargeable)
"""
from uuid import UUID

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin
from app.modules.security.schemas import (
    ResolveIncidentRequest,
    SecurityBlockResponse,
    SecurityIncidentResponse,
    SecuritySummaryResponse,
)
from app.modules.security.service import SecurityService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


@router.get("/summary", response_model=SecuritySummaryResponse)
async def summary(_: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    return await SecurityService(db).summary()


@router.get("/incidents", response_model=list[SecurityIncidentResponse])
async def list_incidents(
    _: CurrentAdmin,
    status: str | None = "open",
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await SecurityService(db).list_incidents(status or None, min(limit, 500))


@router.get("/incidents/{incident_id}", response_model=SecurityIncidentResponse)
async def get_incident(incident_id: UUID, _: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    return await SecurityService(db).get_incident(incident_id)


@router.post("/incidents/{incident_id}/resolve", response_model=SecurityIncidentResponse)
async def resolve_incident(
    incident_id: UUID,
    data: ResolveIncidentRequest,
    admin: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await SecurityService(db).resolve_incident(incident_id, admin, data.note)


@router.get("/blocks", response_model=list[SecurityBlockResponse])
async def list_blocks(_: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    return await SecurityService(db).list_blocks()


@router.post("/users/{user_id}/unblock", response_model=SuccessResponse)
async def unblock_user(user_id: UUID, admin: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    await SecurityService(db).unblock_user(user_id, admin)
    return SuccessResponse(message="Accès rétabli.")


@router.post("/users/{user_id}/ban", response_model=SuccessResponse)
async def ban_user(
    user_id: UUID,
    data: ResolveIncidentRequest,
    admin: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    await SecurityService(db).ban_user(user_id, admin, data.note)
    return SuccessResponse(message="Compte désactivé.")


@router.get("/users/{user_id}/evidence")
async def evidence(user_id: UUID, _: CurrentAdmin, db: AsyncSession = Depends(get_db)):
    data = await SecurityService(db).evidence(user_id)
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f'attachment; filename="preuves_{user_id}.json"'},
    )