"""
Dependencies partagées pour toute l'application.
"""

from typing import Annotated

from fastapi import Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.users.models import User
from app.shared.database.session import DbSession
from app.shared.exceptions.http import UnauthorizedException

# Security scheme pour Swagger UI
security = HTTPBearer(auto_error=False)


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: DbSession = None
) -> User:
    """
    Dépendance pour obtenir l'utilisateur courant.
    
    Accepte le token depuis:
    1. Cookie `access_token` (prioritaire)
    2. Header `Authorization: Bearer <token>`
    """
    # Import local pour éviter circular import
    from app.modules.auth.service import AuthService
    
    # Token depuis cookie ou header
    token = access_token
    if not token and credentials:
        token = credentials.credentials
    
    if not token:
        raise UnauthorizedException(detail="Token d'authentification manquant")
    
    # Vérifier le token
    service = AuthService(db)
    return await service.get_current_user(token)


# Type annoté pour faciliter l'utilisation
CurrentUser = Annotated[User, Depends(get_current_user)]