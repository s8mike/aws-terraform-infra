# Alembic environment: tells Alembic which database to change and which tables the application expects.
# The database address comes from DATABASE_URL, or from "sqlalchemy.url" when a caller sets it (the tests do).
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app import models  # noqa: F401 - importing the models registers every table on Base.metadata
from app.config import DATABASE_URL
from app.database import Base

config = context.config

# Set up logging from alembic.ini without silencing loggers that already exist (pytest, uvicorn).
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# The tables the application expects. "alembic revision --autogenerate" and "alembic check" compare the database with this.
target_metadata = Base.metadata


def get_url() -> str:
    """Return the database address: an explicit setting first, then DATABASE_URL."""
    url = config.get_main_option("sqlalchemy.url") or DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    return url


def run_migrations_offline() -> None:
    """Write the SQL as text instead of running it (no database connection needed)."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and run the migrations."""
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            # SQLite cannot alter tables in place, so it needs "batch" mode; PostgreSQL ignores this.
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()