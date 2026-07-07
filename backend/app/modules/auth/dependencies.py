"""
app/modules/auth/dependencies.py
"""
from typing import Annotated

from fastapi import Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.users.models import User
from app.shared.database.session import get_db
from app.shared.exceptions.http import ForbiddenException, UnauthorizedException
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import UserRole


security = HTTPBearer(auto_error=False)


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Résout l'utilisateur courant depuis cookie ou header Authorization.
    Priorité : cookie > header.
    """
    from app.modules.auth.service import AuthService

    token = access_token
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise UnauthorizedException(detail="Token d'authentification manquant.")

    return await AuthService(db).get_current_user(token)


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Restreint l'accès aux admins uniquement."""
    if not current_user.is_admin:
        raise ForbiddenException(detail="Accès réservé aux administrateurs.")
    return current_user


async def get_current_director(
    current_user: User = Depends(get_current_user),
) -> User:
    """Restreint l'accès aux directeurs de centre."""
    if current_user.role != UserRole.center_director:
        raise ForbiddenException(detail="Accès réservé aux directeurs de centre.")
    return current_user


async def get_current_secretary(
    current_user: User = Depends(get_current_user),
) -> User:
    """Restreint l'accès aux secrétaires de succursale."""
    if current_user.role != UserRole.branch_secretary:
        raise ForbiddenException(detail="Accès réservé aux secrétaires.")
    return current_user


async def get_current_director_or_secretary(
    current_user: User = Depends(get_current_user),
) -> User:
    """Restreint l'accès au staff de centre (directeur ou secrétaire)."""
    if current_user.role not in (UserRole.center_director, UserRole.branch_secretary):
        raise ForbiddenException(detail="Accès réservé au personnel de centre.")
    return current_user



# Annotations pratiques pour les routers
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]

# Annotations pratiques pour les routers
CurrentDirector = Annotated[User, Depends(get_current_director)]
CurrentSecretary = Annotated[User, Depends(get_current_secretary)]
CurrentCenterStaff = Annotated[User, Depends(get_current_director_or_secretary)]