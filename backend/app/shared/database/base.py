"""
Classes de base pour SQLAlchemy.

Ce module contient la classe de base dont tous les modèles héritent,
ainsi que des mixins utilitaires pour ajouter des fonctionnalités communes.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    Classe de base pour tous les modèles SQLAlchemy.
    
    Fournit une configuration commune à tous les modèles.
    """
    
    # Permet d'utiliser des types Python natifs avec Mapped[]
    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
        datetime: DateTime(timezone=True),
    }


class TimestampMixin:
    """
    Mixin qui ajoute les champs created_at et updated_at.
    
    Ces champs sont automatiquement gérés:
    - created_at: défini une seule fois lors de la création
    - updated_at: mis à jour à chaque modification
    
    Example:
        >>> class User(Base, TimestampMixin):
        ...     __tablename__ = "users"
        ...     id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Date de création de l'enregistrement"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Date de dernière modification"
    )


class UUIDMixin:
    """
    Mixin qui ajoute un ID UUID comme clé primaire.
    
    Utilise uuid4() pour générer des IDs uniques et aléatoires.
    
    Example:
        >>> class Organization(Base, UUIDMixin):
        ...     __tablename__ = "organizations"
        ...     name: Mapped[str]
    """
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Identifiant unique UUID"
    )


class TableNameMixin:
    """
    Mixin qui génère automatiquement le nom de table.
    
    Convertit le nom de classe en snake_case et ajoute un 's' pour le pluriel.
    
    Example:
        >>> class UserSubscription(Base, TableNameMixin):
        ...     pass
        >>> # Nom de table généré: "user_subscriptions"
    """
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Génère le nom de table à partir du nom de classe.
        
        Convertit CamelCase en snake_case et pluralise.
        
        Returns:
            str: Nom de table en snake_case pluriel
            
        Example:
            UserSubscription -> user_subscriptions
            Organization -> organizations
        """
        import re
        
        # Convertit CamelCase en snake_case
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Ajoute un 's' pour pluriel (simpliste mais marche pour la plupart des cas)
        if not name.endswith('s'):
            name += 's'
            
        return name


class BaseModel(Base, UUIDMixin, TimestampMixin, TableNameMixin):
    """
    Modèle de base complet combinant tous les mixins.
    
    Utilise cette classe comme base pour la plupart de vos modèles.
    Fournit automatiquement:
    - ID UUID
    - created_at et updated_at
    - Nom de table auto-généré
    
    Example:
        >>> class User(BaseModel):
        ...     email: Mapped[str] = mapped_column(unique=True)
        ...     name: Mapped[str]
        >>> 
        >>> # Équivalent à:
        >>> # - Table: "users"
        >>> # - Colonnes: id (UUID), email, name, created_at, updated_at
    """
    
    __abstract__ = True  # Ne crée pas de table pour cette classe
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convertit le modèle en dictionnaire.
        
        Utile pour sérialisation ou debugging.
        
        Returns:
            dict: Représentation dictionnaire du modèle
            
        Example:
            >>> user = User(email="test@example.com", name="John")
            >>> user.to_dict()
            {'id': UUID('...'), 'email': 'test@example.com', 'name': 'John', ...}
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """
        Représentation string du modèle pour debugging.
        
        Returns:
            str: Représentation lisible du modèle
            
        Example:
            >>> user = User(email="test@example.com")
            >>> print(user)
            User(id=UUID('...'), email='test@example.com')
        """
        columns = ", ".join(
            f"{col.name}={getattr(self, col.name)!r}"
            for col in self.__table__.columns
        )
        return f"{self.__class__.__name__}({columns})"