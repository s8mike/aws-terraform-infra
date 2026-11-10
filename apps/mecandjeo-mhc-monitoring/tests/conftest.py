import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# Configure test environment variables before importing application modules.
TEST_DB_PATH = Path(__file__).resolve().parent / "test_app.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["SECRET_KEY"] = "test-secret-with-at-least-32-characters"
os.environ["JWT_EXPIRE_HOURS"] = "1"

# Every app import must stay below the environment setup above.
from sqlalchemy.orm import Session  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.db.seed_data import seed_reference_data  # noqa: E402
from app.main import app  # noqa: E402


# Recreate database tables before each test to keep test cases independent.
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# Opt-in: seed default reference data for tests that validate operator input against it.
@pytest.fixture
def seeded_reference_data():
    with Session(engine) as db:
        seed_reference_data(db)


# Provide a reusable FastAPI test client to route tests.
@pytest.fixture
def client():
    return TestClient(app)


# Remove the temporary SQLite database after all tests complete.
def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except PermissionError:
            pass