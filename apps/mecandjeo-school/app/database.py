# DB sessions 
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database connection URL
from .config import DATABASE_URL

# Create SQLAlchemy engine. 
# SQLAlchemy uses this engine to communicate with PostgreSQL database.
engine = create_engine(DATABASE_URL)

# Create database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()

# Dependency for database session management
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

####################################################################
## Foundation code for database connection and session management.
######################################################################

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# import os

# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./school.db")

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base = declarative_base()
