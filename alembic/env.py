from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

# --- Ensure "app" can be imported ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import Base  # imports all models
from app.db import models  # noqa: F401 (imported for side effects, register models)
from app.core.config import settings

# Alembic Config object
config = context.config

# --- Database URL from .env via settings ---
# Alembic only works with sync drivers (psycopg2, not asyncpg)
db_url = settings.database_url.replace("asyncpg", "psycopg2")
# Escape % to avoid ConfigParser interpolation errors
safe_url = db_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", safe_url)

# --- Logging ---
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Target metadata for 'autogenerate' ---
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
