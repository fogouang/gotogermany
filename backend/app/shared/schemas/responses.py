"""
Response wrappers standardisés
"""
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.base import BaseSchema

# Type générique pour les données
T = TypeVar('T')


class SuccessResponse(BaseSchema, Generic[T]):
    """
    Response standardisée pour succès
    
    Usage:
        return SuccessResponse(
            data=user,
            message="User créé avec succès"
        )
    """
    
    success: bool = Field(default=True, description="Indicateur de succès")
    message: str | None = Field(default=None, description="Message optionnel")
    data: T | None = Field(default=None, description="Données de la réponse")
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseSchema):
    """
    Response standardisée pour erreurs
    
    Usage:
        return ErrorResponse(
            message="Erreur validation",
            code="VALIDATION_ERROR",
            details={"field": "email"}
        )
    """
    
    success: bool = Field(default=False, description="Indicateur d'échec")
    message: str = Field(..., description="Message d'erreur")
    code: str | None = Field(default=None, description="Code d'erreur")
    details: dict[str, Any] | None = Field(default=None, description="Détails de l'erreur")


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Response paginée standardisée
    
    Usage:
        return PaginatedResponse(
            items=users,
            total=100,
            page=1,
            page_size=20
        )
    """
    
    items: list[T] = Field(..., description="Liste des items")
    total: int = Field(..., description="Nombre total d'items")
    page: int = Field(..., description="Page actuelle")
    page_size: int = Field(..., description="Taille de la page")
    total_pages: int = Field(..., description="Nombre total de pages")
    
    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int = 1,
        page_size: int = 20
    ) -> "PaginatedResponse[T]":
        """
        Helper pour créer une réponse paginée
        """
        total_pages = (total + page_size - 1) // page_size
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )