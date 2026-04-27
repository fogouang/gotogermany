#!/bin/bash
set -e

# ─────────────────────────────────────────────
# DeutschTest — Backend setup (uv)
# Usage : depuis le dossier german-test/
#   chmod +x setup_backend.sh && ./setup_backend.sh
# ─────────────────────────────────────────────

echo "🚀 Setup DeutschTest backend..."

mkdir -p backend
cd backend

# ── Projet uv ──────────────────────────────────
uv init --no-workspace .
rm -f hello.py  # fichier exemple généré par uv

# ── Dépendances ────────────────────────────────
uv add \
  fastapi \
  uvicorn[standard] \
  sqlalchemy[asyncio] \
  asyncpg \
  alembic \
  pydantic-settings \
  pydantic[email] \
  python-jose[cryptography] \
  passlib[bcrypt] \
  python-multipart \
  httpx \
  slowapi

uv add --dev \
  pytest \
  pytest-asyncio \
  httpx \
  ruff

# ── Alembic ────────────────────────────────────
mkdir -p alembic/versions
cat > alembic/env.py << 'EOF'
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.shared.database.base import Base
from app.config import get_settings

# Import all models so Alembic detects them
import app.modules.users.models       # noqa
import app.modules.partners.models    # noqa
import app.modules.promo_codes.models # noqa
import app.modules.exams.models       # noqa
import app.modules.questions.models   # noqa
import app.modules.payments.models    # noqa
import app.modules.exam_access.models # noqa
import app.modules.exam_sessions.models # noqa

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", ""))

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF

cat > alembic/script.py.mako << 'EOF'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
EOF

cat > alembic.ini << 'EOF'
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# ── App structure ───────────────────────────────
mkdir -p app

# ── Shared ─────────────────────────────────────
mkdir -p app/shared/database
mkdir -p app/shared/security
mkdir -p app/shared/schemas
mkdir -p app/shared/exceptions
mkdir -p app/shared/utils
mkdir -p app/shared/enums

touch app/shared/__init__.py
touch app/shared/database/__init__.py
touch app/shared/security/__init__.py
touch app/shared/schemas/__init__.py
touch app/shared/exceptions/__init__.py
touch app/shared/utils/__init__.py
touch app/shared/enums/__init__.py

# ── Modules ─────────────────────────────────────
mkdir -p app/modules

create_module() {
  local name=$1
  mkdir -p app/modules/$name
  touch app/modules/$name/__init__.py
  touch app/modules/$name/models.py
  touch app/modules/$name/schemas.py
  touch app/modules/$name/repository.py
  touch app/modules/$name/service.py
  touch app/modules/$name/router.py
}

# Auth (cas spécial — pas de models propres)
mkdir -p app/modules/auth
touch app/modules/auth/__init__.py
touch app/modules/auth/schemas.py
touch app/modules/auth/service.py
touch app/modules/auth/router.py
touch app/modules/auth/dependencies.py

# Métier
create_module "users"
create_module "partners"
create_module "promo_codes"
create_module "exams"
create_module "questions"
create_module "payments"
create_module "exam_access"
create_module "exam_sessions"
create_module "admin"

touch app/modules/__init__.py

# ── Scripts ─────────────────────────────────────
mkdir -p scripts
touch scripts/seed_db.py
touch scripts/create_admin.py
touch scripts/import_exam.py

# ── Tests ───────────────────────────────────────
mkdir -p tests/test_auth
mkdir -p tests/test_payments
mkdir -p tests/test_exams
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_auth/__init__.py
touch tests/test_payments/__init__.py
touch tests/test_exams/__init__.py

# ── Storage ─────────────────────────────────────
mkdir -p storage/audio
mkdir -p storage/temp

# ── Fichiers racine ─────────────────────────────
touch .env.example
touch .gitignore

# ── .env.example ────────────────────────────────
cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/deutschtest

# Security
SECRET_KEY=changeme-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# My-CoolPay
MYCOOLPAY_PUBLIC_KEY=
MYCOOLPAY_PRIVATE_KEY=
MYCOOLPAY_BASE_URL=https://my-coolpay.com/api
MYCOOLPAY_CALLBACK_URL=https://yourdomain.com/api/v1/payments/webhook

# App
APP_ENV=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000
EOF

# ── .gitignore ──────────────────────────────────
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
.venv/
*.egg-info/
.pytest_cache/
.ruff_cache/
storage/audio/*
storage/temp/*
!storage/audio/.gitkeep
!storage/temp/.gitkeep
EOF

touch storage/audio/.gitkeep
touch storage/temp/.gitkeep

# ── app/__init__.py ──────────────────────────────
touch app/__init__.py

# ── app/config.py ───────────────────────────────
cat > app/config.py << 'EOF'
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # My-CoolPay
    MYCOOLPAY_PUBLIC_KEY: str = ""
    MYCOOLPAY_PRIVATE_KEY: str = ""
    MYCOOLPAY_BASE_URL: str = "https://my-coolpay.com/api"
    MYCOOLPAY_CALLBACK_URL: str = ""

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
EOF

# ── app/shared/database/base.py ─────────────────
cat > app/shared/database/base.py << 'EOF'
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
EOF

# ── app/shared/database/session.py ──────────────
cat > app/shared/database/session.py << 'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
EOF

# ── app/shared/schemas/base.py ───────────────────
cat > app/shared/schemas/base.py << 'EOF'
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
EOF

# ── app/shared/schemas/responses.py ─────────────
cat > app/shared/schemas/responses.py << 'EOF'
from typing import Generic, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: T | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Any = None
EOF

# ── app/main.py ──────────────────────────────────
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="DeutschTest API",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (à décommenter au fur et à mesure)
# from app.modules.auth.router import router as auth_router
# from app.modules.users.router import router as users_router
# from app.modules.exams.router import router as exams_router
# from app.modules.payments.router import router as payments_router
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
# app.include_router(exams_router, prefix="/api/v1/exams", tags=["exams"])
# app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
EOF

echo ""
echo "✅ Backend DeutschTest généré dans german-test/backend/"
echo ""
echo "Prochaines étapes :"
echo "  cd backend"
echo "  cp .env.example .env  # puis éditer avec tes vraies valeurs"
echo "  uv run uvicorn app.main:app --reload"