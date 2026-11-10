from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL


# Fail early when the database connection string has not been configured.
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

# Create the SQLAlchemy engine used to communicate with PostgreSQL.
engine = create_engine(DATABASE_URL)

# Create a reusable database session factory for request handlers.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class used by all SQLAlchemy model definitions.
Base = declarative_base()


# FastAPI dependency that opens and closes a database session per request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Phase 8: verify connectivity and create local-development tables when enabled.
def initialize_database() -> None:
    """Create registered tables only for explicitly enabled local development."""
    from . import models  # noqa: F401 - imports model classes into Base metadata.

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    Base.metadata.create_all(bind=engine)
