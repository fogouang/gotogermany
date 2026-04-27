"""
HTTP Exceptions standardisées
"""
from typing import Any
from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Ressource introuvable (404)
    
    Usage:
        raise NotFoundException(resource="User", identifier="user-id-123")
    """
    
    def __init__(
        self,
        resource: str,
        identifier: str | None = None,
        detail: str | None = None
    ):
        if detail is None:
            detail = f"{resource} introuvable"
            if identifier:
                detail += f" (id: {identifier})"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UnauthorizedException(HTTPException):
    """
    Non authentifié (401)
    
    Usage:
        raise UnauthorizedException()
        raise UnauthorizedException(detail="Token expiré")
    """
    
    def __init__(self, detail: str = "Authentification requise"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    """
    Accès interdit (403)
    
    Usage:
        raise ForbiddenException()
        raise ForbiddenException(detail="Rôle admin requis")
    """
    
    def __init__(self, detail: str = "Accès interdit"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BadRequestException(HTTPException):
    """
    Requête invalide (400)
    
    Usage:
        raise BadRequestException(detail="Email déjà utilisé")
    """
    
    def __init__(self, detail: str, errors: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": detail, "errors": errors} if errors else detail
        )


class ConflictException(HTTPException):
    """
    Conflit (409) - Ressource déjà existante
    
    Usage:
        raise ConflictException(resource="User", field="email")
    """
    
    def __init__(
        self,
        resource: str,
        field: str | None = None,
        detail: str | None = None
    ):
        if detail is None:
            detail = f"{resource} existe déjà"
            if field:
                detail += f" ({field})"
        
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )