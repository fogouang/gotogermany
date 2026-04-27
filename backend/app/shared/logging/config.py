"""
Configuration logging centralisée
"""
import logging
import sys
from pythonjsonlogger import jsonlogger

from app.config import get_settings

settings = get_settings()


def setup_logging():
    """
    Configure logging pour l'application
    
    - Development: Logs lisibles avec couleurs
    - Production: Logs JSON structurés
    """
    
    # Niveau de log selon environnement
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Déterminer l'environnement (ajouter ENVIRONMENT dans config si manquant)
    environment = getattr(settings, "ENVIRONMENT", "development")
    
    if environment == "production":
        # Production: Format JSON
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            timestamp=True
        )
    else:
        # Development: Format lisible
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Réduire verbosité de certains loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.DEBUG else logging.INFO
    )
    
    return root_logger


# Logger par défaut pour l'app
logger = logging.getLogger("Deucht")