import pytest
from sqlalchemy.orm import Session

from app.auth import ROLE_ADMIN
from app.database import engine
from app.db import bootstrap
from app.models import Crane, User

ADMIN_EMAIL = "admin@example.test"
ADMIN_PASSWORD = "a-long-local-password-1"


def configure(monkeypatch, email=ADMIN_EMAIL, password=ADMIN_PASSWORD):
    monkeypatch.setattr(bootstrap, "BOOTSTRAP_ADMIN_EMAIL", email)
    monkeypatch.setattr(bootstrap, "BOOTSTRAP_ADMIN_PASSWORD", password)


def test_bootstrap_creates_active_admin_with_hashed_password(monkeypatch):
    configure(monkeypatch, email="Admin@Example.test")
    bootstrap.run_bootstrap()
    with Session(engine) as db:
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).one()
        assert admin.role == ROLE_ADMIN
        assert admin.is_active is True
        assert admin.password_hash != ADMIN_PASSWORD


def test_bootstrap_is_idempotent_and_never_overwrites_existing_admin(monkeypatch):
    configure(monkeypatch)
    bootstrap.run_bootstrap()
    with Session(engine) as db:
        first_hash = db.query(User).filter(User.email == ADMIN_EMAIL).one().password_hash

    configure(monkeypatch, password="a-different-long-password-2")
    bootstrap.run_bootstrap()
    with Session(engine) as db:
        users = db.query(User).filter(User.email == ADMIN_EMAIL).all()
        assert len(users) == 1
        assert users[0].password_hash == first_hash


def test_bootstrap_skips_admin_when_not_configured(monkeypatch):
    configure(monkeypatch, email=None, password=None)
    bootstrap.run_bootstrap()
    with Session(engine) as db:
        assert db.query(User).count() == 0


def test_bootstrap_rejects_short_password(monkeypatch):
    configure(monkeypatch, password="short")
    with pytest.raises(RuntimeError):
        bootstrap.run_bootstrap()


def test_bootstrap_seeds_sample_cranes_once_when_enabled(monkeypatch):
    configure(monkeypatch, email=None, password=None)
    monkeypatch.setattr(bootstrap, "SEED_SAMPLE_DATA", True)
    bootstrap.run_bootstrap()
    bootstrap.run_bootstrap()
    with Session(engine) as db:
        assert db.query(Crane).count() == 3


def test_bootstrap_skips_sample_cranes_by_default(monkeypatch):
    configure(monkeypatch, email=None, password=None)
    monkeypatch.setattr(bootstrap, "SEED_SAMPLE_DATA", False)
    bootstrap.run_bootstrap()
    with Session(engine) as db:
        assert db.query(Crane).count() == 0