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
from fastapi import WebSocket, WebSocketDisconnect


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

async def get_current_user_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Résout l'utilisateur pour une route WebSocket. NE PAS appeler
    websocket.close() ici : cette dépendance s'exécute AVANT que la route
    n'ait appelé websocket.accept() (accept() est dans le corps de chaque
    route, pas ici) — fermer un socket jamais accepté lève une
    RuntimeError et pollue les logs d'un traceback, même si Starlette
    finit quand même par rejeter proprement la connexion (403) par
    défaut quand une exception remonte avant l'accept.
    """
    from app.modules.auth.service import AuthService

    token = websocket.cookies.get("access_token") or websocket.query_params.get("token")
    if not token:
        raise WebSocketDisconnect(code=4401)

    try:
        return await AuthService(db).get_current_user(token)
    except UnauthorizedException:
        raise WebSocketDisconnect(code=4401)
    
    
# async def get_current_user_ws(
#     websocket: WebSocket,
#     db: AsyncSession = Depends(get_db),
# ) -> User:
#     """Variante WebSocket de get_current_user.

#     MODIF : accepte désormais le token soit via le cookie access_token,
#     soit via un paramètre de requête ?token=... — un client WebSocket
#     natif ne peut pas fixer de header Authorization à la connexion, et
#     le cookie access_token (posé côté frontend via useCookie()) n'est
#     pas garanti d'atteindre le domaine du backend si frontend et backend
#     sont sur des origines différentes (contrairement au REST, qui envoie
#     le token en header Bearer via OpenAPI.TOKEN, jamais via ce cookie).
#     Le query param est donc la voie fiable pour un WS cross-origin.
#     """
#     from app.modules.auth.service import AuthService

#     token = websocket.cookies.get("access_token") or websocket.query_params.get("token")
#     if not token:
#         await websocket.close(code=4401)
#         raise WebSocketDisconnect(code=4401)

#     try:
#         return await AuthService(db).get_current_user(token)
#     except UnauthorizedException:
#         await websocket.close(code=4401)
#         raise WebSocketDisconnect(code=4401)

async def get_current_ambassador(
    current_user: User = Depends(get_current_user),
) -> User:
    """Restreint l'accès aux ambassadeurs désignés par l'admin."""
    if not current_user.is_ambassador:
        raise ForbiddenException(detail="Accès réservé aux ambassadeurs.")
    return current_user




# Annotations pratiques pour les routers
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]

# Annotations pratiques pour les routers
CurrentDirector = Annotated[User, Depends(get_current_director)]
CurrentSecretary = Annotated[User, Depends(get_current_secretary)]
CurrentCenterStaff = Annotated[User, Depends(get_current_director_or_secretary)]

CurrentAmbassador = Annotated[User, Depends(get_current_ambassador)]