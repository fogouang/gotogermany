"""
Gestion des mots de passe (hashing + vérification)
"""
from passlib.context import CryptContext

from app.shared.logging import logger

# Configuration bcrypt avec truncate_error=False
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__default_rounds=10,  # Ajustez pour perf
    truncate_error=False
)


def hash_password(password: str) -> str:
    """
    Hasher un mot de passe avec bcrypt
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        Hash bcrypt du mot de passe
    """
    logger.debug("Hashing password")
    
    # Tronquer à 72 bytes si nécessaire (bcrypt limite)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
        logger.warning("Password truncated to 72 bytes for bcrypt")
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifier un mot de passe contre son hash
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash bcrypt du mot de passe
    
    Returns:
        True si le mot de passe correspond, False sinon
    """
    try:
        # Tronquer si nécessaire
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        is_valid = pwd_context.verify(plain_password, hashed_password)
        if is_valid:
            logger.debug("Password verification successful")
        else:
            logger.debug("Password verification failed")
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False