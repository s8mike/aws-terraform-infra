# Phase 9: tests that operator task and delay inputs must match active reference data.
import pytest

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import Crane, ReferenceData, User

pytestmark = pytest.mark.usefixtures("seeded_reference_data")

PASSWORD = "Securepass123!"


# Create a crane and an operator, log in, and start a shift; returns auth headers and the shift.
def setup_operator_shift(client):
    db = SessionLocal()
    try:
        db.add(Crane(code="MHC-01", mhc_number="MHC-01", name="Mobile Harbour Crane 01", is_active=True))
        db.add(User(email="operator@example.com", full_name="Operator User", password_hash=get_password_hash(PASSWORD), role="operator", is_active=True))
        db.commit()
    finally:
        db.close()
    login = client.post("/api/auth/login", json={"email": "operator@example.com", "password": PASSWORD})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    shift = client.post(
        "/api/shifts/start",
        headers=headers,
        json={"mhc_number": "MHC-01", "shift_code": "A", "started_at": "2026-08-21T08:00:00"},
    ).json()
    return headers, shift


# Start a task with valid defaults that individual tests can override.
def start_task(client, headers, shift_id, **overrides):
    payload = {
        "shift_id": shift_id,
        "nature_of_work": "discharging",
        "working_area": "deck_free_bay",
        "started_at": "2026-08-21T08:15:00",
    }
    payload.update(overrides)
    return client.post("/api/task-logs/start", headers=headers, json=payload)


# Start a delay with valid defaults that individual tests can override.
def start_delay(client, headers, task_id, **overrides):
    payload = {
        "task_log_id": task_id,
        "delay_type": "awaiting_trucks",
        "started_at": "2026-08-21T08:30:00",
    }
    payload.update(overrides)
    return client.post("/api/delay-logs/start", headers=headers, json=payload)


# Purpose: verify an unknown work type is rejected and leaves no half-created active task behind.
def test_task_rejects_unknown_nature_of_work(client):
    headers, shift = setup_operator_shift(client)

    rejected = start_task(client, headers, shift["id"], nature_of_work="not_a_real_work_type")
    accepted = start_task(client, headers, shift["id"])

    assert rejected.status_code == 400
    assert accepted.status_code == 201


# Purpose: verify an unknown working area is rejected.
def test_task_rejects_unknown_working_area(client):
    headers, shift = setup_operator_shift(client)

    rejected = start_task(client, headers, shift["id"], working_area="not_a_real_area")

    assert rejected.status_code == 400


# Purpose: verify a retired area (plain "deck") is rejected, since only the free-bay and across-heights variants exist.
def test_task_rejects_retired_plain_deck_area(client):
    headers, shift = setup_operator_shift(client)

    rejected = start_task(client, headers, shift["id"], working_area="deck")

    assert rejected.status_code == 400


# Purpose: verify accepted values are stored in their normalized lowercase form for consistent reporting.
def test_task_values_are_normalized(client):
    headers, shift = setup_operator_shift(client)

    response = start_task(client, headers, shift["id"], nature_of_work="DISCHARGING", working_area=" Deck_Free_Bay ")

    assert response.status_code == 201
    body = response.json()
    assert body["nature_of_work"] == "discharging"
    assert body["working_area"] == "deck_free_bay"


# Purpose: verify a value an admin has retired can no longer be chosen.
def test_task_rejects_deactivated_reference_value(client):
    headers, shift = setup_operator_shift(client)
    db = SessionLocal()
    try:
        row = db.query(ReferenceData).filter_by(category="working_area", code="deck_free_bay").one()
        row.is_active = False
        db.commit()
    finally:
        db.close()

    rejected = start_task(client, headers, shift["id"])

    assert rejected.status_code == 400


# Purpose: verify an unknown delay type is rejected and does not block a valid retry.
def test_delay_rejects_unknown_delay_type(client):
    headers, shift = setup_operator_shift(client)
    task = start_task(client, headers, shift["id"]).json()

    rejected = start_delay(client, headers, task["id"], delay_type="made_up_delay")
    accepted = start_delay(client, headers, task["id"])

    assert rejected.status_code == 400
    assert accepted.status_code == 201


# Purpose: verify local delay causes can still be captured as free text under the standard other_delay type.
def test_delay_accepts_custom_delay_type_label(client):
    headers, shift = setup_operator_shift(client)
    task = start_task(client, headers, shift["id"]).json()

    response = start_delay(client, headers, task["id"], delay_type="other_delay", custom_delay_type="Gate system outage")

    assert response.status_code == 201
    assert response.json()["custom_delay_type"] == "Gate system outage"