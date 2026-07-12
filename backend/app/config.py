from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Chemin absolu vers le .env à la racine de backend/
ENV_FILE = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    MYCOOLPAY_PUBLIC_KEY: str = ""
    MYCOOLPAY_PRIVATE_KEY: str = ""
    MYCOOLPAY_BASE_URL: str = "https://my-coolpay.com/api"
    MYCOOLPAY_CALLBACK_URL: str = ""
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    PAWAPAY_API_TOKEN: str
    PAWAPAY_SANDBOX: bool = True
    
    # AI Correction Configuration
    AI_PROVIDER: str = "gemini"  # Options: "grok", "gemini", "claude"
    # Gemini (Google)
    
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

@lru_cache
def get_settings() -> Settings:
    return Settings()