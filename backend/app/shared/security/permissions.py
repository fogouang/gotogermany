"""
Gestion des permissions par rôle.
"""

from functools import wraps
from typing import Callable

from fastapi import Depends

from app.modules.users.models import User
from app.shared.enums import UserRole
from app.shared.exceptions.http import ForbiddenException


def require_roles(*allowed_roles: UserRole) -> Callable:
    """
    Décorateur pour restreindre l'accès selon les rôles.
    
    Args:
        *allowed_roles: Rôles autorisés
        
    Returns:
        Décorateur de fonction
        
    Example:
        >>> @require_roles(UserRole.PLATFORM_ADMIN)
        >>> async def admin_only_endpoint(current_user: User = Depends(get_current_user)):
        ...     return {"message": "Admin access"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Récupérer current_user depuis les kwargs
            current_user: User | None = kwargs.get("current_user")
            
            if current_user is None:
                raise ForbiddenException(detail="Utilisateur non authentifié")
            
            if current_user.role not in allowed_roles:
                raise ForbiddenException(
                    detail=f"Rôle requis: {', '.join(r.value for r in allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def is_platform_admin(user: User) -> bool:
    """Vérifie si l'utilisateur est admin plateforme."""
    return user.role == UserRole.PLATFORM_ADMIN


def is_org_admin(user: User) -> bool:
    """Vérifie si l'utilisateur est admin organisation."""
    return user.role == UserRole.ORG_ADMIN


def is_teacher(user: User) -> bool:
    """Vérifie si l'utilisateur est enseignant."""
    return user.role == UserRole.TEACHER


def is_student(user: User) -> bool:
    """Vérifie si l'utilisateur est étudiant."""
    return user.role == UserRole.STUDENT


def can_manage_organization(user: User, organization_id: str) -> bool:
    """
    Vérifie si l'utilisateur peut gérer une organisation.
    
    Args:
        user: Utilisateur courant
        organization_id: ID de l'organisation
        
    Returns:
        True si autorisé
    """
    # Admin plateforme peut tout gérer
    if is_platform_admin(user):
        return True
    
    # Admin org peut gérer sa propre org
    if is_org_admin(user):
        # Vérifier que l'user est admin de cette org
        return any(
            str(org.id) == organization_id 
            for org in user.managed_organizations
        )
    
    return False


def can_correct_expressions(user: User, organization_id: str | None = None) -> bool:
    """
    Vérifie si l'utilisateur peut corriger des expressions.
    
    Args:
        user: Utilisateur courant
        organization_id: ID de l'organisation (optionnel)
        
    Returns:
        True si autorisé
    """
    # Admin plateforme peut tout corriger
    if is_platform_admin(user):
        return True
    
    # Admin org peut corriger dans son org
    if is_org_admin(user) and organization_id:
        return can_manage_organization(user, organization_id)
    
    # Teacher peut corriger dans son org
    if is_teacher(user) and organization_id:
        return any(
            str(org.id) == organization_id 
            for org in user.teaching_at_organizations
        )
    
    return False