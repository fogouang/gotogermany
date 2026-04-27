"""
app/modules/users/router.py
"""
from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.users.schemas import (
    UserAdminResponse,
    UserChangePasswordRequest,
    UserMeResponse,
    UserUpdateRequest,
)
from app.modules.users.service import UserService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


# ── User (self) ──────────────────────────────

@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: CurrentUser):
    """Profil de l'utilisateur connecté."""
    return current_user


@router.patch("/me", response_model=UserMeResponse)
async def update_me(
    data: UserUpdateRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Mise à jour du profil."""
    return await UserService(db).update_me(current_user, data)


@router.post("/me/change-password", response_model=SuccessResponse)
async def change_password(
    data: UserChangePasswordRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Changement de mot de passe."""
    await UserService(db).change_password(current_user, data)
    return SuccessResponse(message="Mot de passe modifié avec succès.")


# ── Admin ────────────────────────────────────

@router.get("", response_model=list[UserAdminResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les utilisateurs — admin uniquement."""
    return await UserService(db).get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserAdminResponse)
async def get_user(
    user_id: UUID,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Détail d'un utilisateur — admin uniquement."""
    return await UserService(db).get_by_id(user_id)


@router.patch("/{user_id}/toggle-active", response_model=UserAdminResponse)
async def toggle_active(
    user_id: UUID,
    current_admin: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Active ou désactive un compte — admin uniquement."""
    return await UserService(db).toggle_active(user_id, current_admin)


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: UUID,
    current_admin: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Supprime un utilisateur — admin uniquement."""
    await UserService(db).delete(user_id, current_admin)
    return SuccessResponse(message="Utilisateur supprimé.")