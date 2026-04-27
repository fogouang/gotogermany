"""
Gestion des tokens JWT (création & décodage).

Utilise python-jose pour générer et valider les JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Crée un JWT access token.
    
    Args:
        data: Données à encoder dans le token (ex: {"sub": user_id})
        expires_delta: Durée de validité custom (optionnel)
        
    Returns:
        str: JWT token encodé
        
    Example:
        >>> token = create_access_token({"sub": "user-uuid-123"})
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    to_encode = data.copy()
    
    # Calcul expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encodage JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Décode et valide un JWT access token.
    
    Args:
        token: JWT token à décoder
        
    Returns:
        dict | None: Payload décodé si valide, None sinon
        
    Example:
        >>> token = create_access_token({"sub": "user-123"})
        >>> payload = decode_access_token(token)
        >>> print(payload)
        {'sub': 'user-123', 'exp': 1734567890}
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None