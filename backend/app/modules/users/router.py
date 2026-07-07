"""
app/modules/users/router.py
"""
from uuid import UUID
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import (
    CurrentAdmin,
    CurrentUser,
    CurrentDirector,
    CurrentSecretary,
)
from app.modules.users.schemas import (
    UserAdminResponse,
    UserChangePasswordRequest,
    UserMeResponse,
    UserUpdateRequest,
    DirectorCreateRequest,
    SecretaryCreateRequest,
    StudentCreateRequest,
    StudentTargetUpdateRequest,
    StudentResponse,
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


@router.get("/me/credits", response_model=dict)
async def get_my_credits(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Retourne le solde de crédits IA de l'utilisateur."""
    return {
        "ai_credits": current_user.ai_credits,
        "can_correct": current_user.ai_credits > 0,
    }


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


@router.get("/secretaries", response_model=list[UserAdminResponse])
async def list_secretaries(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Liste les secrétaires du centre du directeur connecté."""
    return await UserService(db).list_secretaries_for_director(current_director)

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


@router.post("/directors", response_model=UserAdminResponse, status_code=201)
async def create_director(
    data: DirectorCreateRequest,
    _: CurrentAdmin = None,
    db: AsyncSession = Depends(get_db),
):
    """Créer un compte center_director — admin ITIA, après paiement/activation licence."""
    return await UserService(db).create_director(data)


# ── Directeur ─────────────────────────────────
@router.post("/secretaries", response_model=UserAdminResponse, status_code=201)
async def create_secretary(
    data: SecretaryCreateRequest,
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Le directeur crée un compte secrétaire pour une de ses succursales."""
    return await UserService(db).create_secretary(data, current_director)


@router.get("/students/by-center", response_model=list[StudentResponse])
async def list_students_by_center(
    current_director: CurrentDirector,
    db: AsyncSession = Depends(get_db),
):
    """Vue consolidée de tous les étudiants du centre, toutes succursales confondues."""
    return await UserService(db).list_students_for_director(current_director)


# ── Secrétaire ────────────────────────────────
@router.post("/students", response_model=StudentResponse, status_code=201)
async def create_student(
    data: StudentCreateRequest,
    current_secretary: CurrentSecretary,
    db: AsyncSession = Depends(get_db),
):
    """La secrétaire crée un compte étudiant — bloqué si quota licence atteint."""
    return await UserService(db).create_student(data, current_secretary)


@router.patch("/students/{student_id}/target", response_model=StudentResponse)
async def update_student_target(
    student_id: UUID,
    data: StudentTargetUpdateRequest,
    current_secretary: CurrentSecretary,
    db: AsyncSession = Depends(get_db),
):
    """Modifie l'examen/niveau ciblé d'un étudiant — sans consommer une nouvelle place."""
    return await UserService(db).update_student_target(student_id, data, current_secretary)


@router.get("/students/by-branch", response_model=list[StudentResponse])
async def list_students_by_branch(
    current_secretary: CurrentSecretary,
    db: AsyncSession = Depends(get_db),
):
    """Liste des étudiants de la succursale de la secrétaire connectée."""
    return await UserService(db).list_students_for_secretary(current_secretary)