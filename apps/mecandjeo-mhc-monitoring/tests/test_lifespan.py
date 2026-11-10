# Phase 11: tests that start-up work (create tables, run bootstrap) follows its two settings independently.
import importlib

from fastapi.testclient import TestClient

main_module = importlib.import_module("app.main")


# Start the app (which runs its start-up code) with the given settings and report which start-up steps ran, in order.
def start_app(monkeypatch, create_tables: bool, bootstrap: bool) -> list[str]:
    calls: list[str] = []
    monkeypatch.setattr(main_module, "AUTO_CREATE_SCHEMA", create_tables)
    monkeypatch.setattr(main_module, "RUN_BOOTSTRAP", bootstrap)
    monkeypatch.setattr(main_module, "initialize_database", lambda: calls.append("create_tables"))
    monkeypatch.setattr(main_module, "run_bootstrap", lambda: calls.append("bootstrap"))
    with TestClient(main_module.app):
        pass
    return calls


# Purpose: verify nothing runs at start-up when both settings are off (the production setting).
def test_start_up_does_nothing_when_both_settings_are_off(monkeypatch):
    assert start_app(monkeypatch, create_tables=False, bootstrap=False) == []


# Purpose: verify the bootstrap can run on a schema built by migrations, without creating tables directly.
def test_bootstrap_alone_does_not_create_tables(monkeypatch):
    assert start_app(monkeypatch, create_tables=False, bootstrap=True) == ["bootstrap"]


# Purpose: verify table creation does not imply bootstrap any more (the two settings are independent).
def test_create_tables_alone_does_not_run_bootstrap(monkeypatch):
    assert start_app(monkeypatch, create_tables=True, bootstrap=False) == ["create_tables"]


# Purpose: verify that with both on, the tables are created before the bootstrap needs them.
def test_tables_are_created_before_the_bootstrap_runs(monkeypatch):
    assert start_app(monkeypatch, create_tables=True, bootstrap=True) == ["create_tables", "bootstrap"]