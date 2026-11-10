# Phase 11: tests that the migrations build exactly the schema the models describe, can be undone, and fit existing databases.
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from app.database import Base

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Every table the application defines (the migration history must create all of them).
EXPECTED_TABLES = {
    "admin_profiles",
    "audit_logs",
    "cranes",
    "delay_logs",
    "manager_profiles",
    "operator_profiles",
    "performance_snapshots",
    "reference_data",
    "report_exports",
    "shifts",
    "task_logs",
    "users",
    "working_conditions",
}


# Alembic settings that point at a throwaway SQLite file, so the database used by the other tests is untouched.
def alembic_config(database_path: Path) -> Config:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    return config


# The names of the tables that exist in a database file.
def table_names(database_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


# Purpose: verify the migrations create every table, and that nothing differs from the models afterwards.
def test_migrations_build_the_schema_the_models_describe(tmp_path):
    config = alembic_config(tmp_path / "fresh.db")

    command.upgrade(config, "head")

    assert table_names(tmp_path / "fresh.db") == EXPECTED_TABLES | {"alembic_version"}
    # "check" raises an error listing the differences if the models and the database no longer match.
    command.check(config)


# Purpose: verify the migration can be undone completely.
def test_downgrade_removes_every_table(tmp_path):
    config = alembic_config(tmp_path / "undo.db")
    command.upgrade(config, "head")

    command.downgrade(config, "base")

    assert table_names(tmp_path / "undo.db") == {"alembic_version"}


# Purpose: verify running the migrations again changes nothing (the compose migrate job runs on every start).
def test_upgrade_is_safe_to_repeat(tmp_path):
    config = alembic_config(tmp_path / "again.db")

    command.upgrade(config, "head")
    command.upgrade(config, "head")

    assert table_names(tmp_path / "again.db") == EXPECTED_TABLES | {"alembic_version"}


# Purpose: verify the history is a single straight line, so there is always exactly one "latest" revision.
def test_history_has_a_single_head(tmp_path):
    scripts = ScriptDirectory.from_config(alembic_config(tmp_path / "unused.db"))

    assert scripts.get_heads() == ["0001"]
    assert scripts.get_revision("0001").down_revision is None


# Purpose: verify a database built earlier by create_all can be adopted with "stamp" without losing its data.
def test_stamp_adopts_an_existing_database_without_changing_it(tmp_path):
    database_path = tmp_path / "existing.db"
    config = alembic_config(database_path)
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO cranes (code, mhc_number, name, is_active, created_at, updated_at) "
                 "VALUES ('MHC-01', 'MHC-01', 'Crane 01', 1, '2026-10-07 06:00:00', '2026-10-07 06:00:00')")
        )
    engine.dispose()

    command.stamp(config, "head")
    command.upgrade(config, "head")
    command.check(config)

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM cranes")).scalar() == 1
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0001"
    engine.dispose()


# Purpose: verify upgrading a database that already has the tables but was never stamped fails loudly instead of corrupting it.
def test_upgrade_refuses_an_unstamped_existing_database(tmp_path):
    database_path = tmp_path / "unstamped.db"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    Base.metadata.create_all(engine)
    engine.dispose()

    with pytest.raises(Exception, match="already exists"):
        command.upgrade(alembic_config(database_path), "head")