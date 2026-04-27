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


# Annotations pratiques pour les routers
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]