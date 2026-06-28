# app/modules/settings/router.py
from fastapi.routing import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.settings.service import AppSettingsService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()

@router.get("/free-access")
async def get_free_access_mode(
    _: CurrentUser,  # ← tous les users connectés peuvent lire
    db: AsyncSession = Depends(get_db),
):
    is_free = await AppSettingsService(db).is_free_access_mode()
    return {"free_access_mode": is_free}

@router.post("/free-access/toggle", response_model=SuccessResponse)
async def toggle_free_access_mode(
    _: CurrentAdmin,  # ← admin uniquement
    db: AsyncSession = Depends(get_db),
):
    service = AppSettingsService(db)
    current = await service.is_free_access_mode()
    new_value = "false" if current else "true"
    await service.set(
        key="free_access_mode",
        value=new_value,
        description="Ouvre tous les sujets à tous les users sans paiement"
    )
    status = "activé" if new_value == "true" else "désactivé"
    return SuccessResponse(message=f"Mode accès libre {status}.")