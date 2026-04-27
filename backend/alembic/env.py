"""
alembic/env.py
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ── Config Alembic ────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import tous les models pour autogenerate ──────────
import app.shared.database.registry  # noqa: F401

from app.shared.database.base import Base
from app.config import get_settings

settings = get_settings()

target_metadata = Base.metadata

# URL async (asyncpg) — pour les migrations online
async_url = settings.DATABASE_URL
if "+asyncpg" not in async_url and "postgresql" in async_url:
    async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")

# URL sync (psycopg2) — pour les migrations offline
sync_url = async_url.replace("+asyncpg", "")

config.set_main_option("sqlalchemy.url", async_url)


# ── Migrations offline ────────────────────────────────
def run_migrations_offline() -> None:
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Migrations online (async) ─────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()