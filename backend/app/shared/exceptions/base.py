"""
Exceptions custom de base
"""


class AppException(Exception):
    """
    Exception de base pour toute l'application
    
    Usage:
        raise AppException(
            message="Une erreur est survenue",
            code="APP_ERROR"
        )
    """
    
    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict | None = None
    ):
        self.message = message
        self.code = code or "APP_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ValidationException(AppException):
    """
    Exception pour erreurs de validation
    
    Usage:
        raise ValidationException(
            message="Email invalide",
            code="INVALID_EMAIL",
            details={"field": "email", "value": "bad@"}
        )
    """
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )


class BusinessLogicException(AppException):
    """
    Exception pour erreurs de logique métier
    
    Usage:
        raise BusinessLogicException(
            message="Crédits insuffisants",
            code="INSUFFICIENT_CREDITS",
            details={"required": 5, "available": 2}
        )
    """
    pass


class DatabaseException(AppException):
    """
    Exception pour erreurs database
    """
    
    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details={"original_error": str(original_error)} if original_error else {}
        )