# Phase 4: tests for operator shift, task, delay, and condition workflows.
import pytest
from app.database import SessionLocal
from app.auth import get_password_hash
from app.models import Crane
from app.models import User

pytestmark = pytest.mark.usefixtures("seeded_reference_data")

# Helper creates a physical MHC record so operators can select it by MHC number.
def seed_crane(mhc_number: str = "MHC-01"):
    db = SessionLocal()
    try:
        crane = Crane(
            code=mhc_number,
            mhc_number=mhc_number,
            name=f"Mobile Harbour Crane {mhc_number}",
            is_active=True,
        )
        db.add(crane)
        db.commit()
        db.refresh(crane)
        return crane
    finally:
        db.close()


# Helper registers a user through the public auth API.
def register_user(client, email: str, role: str):
    if role != "operator":
        db = SessionLocal()
        try:
            db.add(User(email=email, full_name="Workflow User", password_hash=get_password_hash("Securepass123!"), role=role, is_active=True))
            db.commit()
        finally:
            db.close()
        return None
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "full_name": "Workflow User",
            "password": "Securepass123!",
            "role": role,
            "is_active": True,
        },
    )


# Helper logs in and returns a bearer authorization header.
def login_header(client, email: str):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "Securepass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Purpose: verify a complete operator workflow from shift start to shift end.
def test_operator_can_complete_shift_task_delay_and_condition_workflow(client):
    seed_crane()
    register_user(client, "john-Doe@example.com", "operator")
    headers = login_header(client, "john-Doe@example.com")

    shift_response = client.post(
        "/api/shifts/start",
        headers=headers,
        json={
            "mhc_number": "MHC-01",
            "shift_code": "A",
            "started_at": "2026-08-21T08:00:00",
            "notes": "Operator started Shift A",
        },
    )
    assert shift_response.status_code == 201
    shift = shift_response.json()
    assert shift["shift_code"] == "A"
    assert shift["mhc_number"] == "MHC-01"

    condition_response = client.post(
        "/api/working-conditions/",
        headers=headers,
        json={
            "shift_id": shift["id"],
            "weather_condition": "clear",
            "visibility": "good",
            "wind_condition": "calm",
            "deck_condition": "dry",
            "congestion_level": "medium",
            "notes": "Normal start-of-shift conditions",
        },
    )
    assert condition_response.status_code == 201

    task_response = client.post(
        "/api/task-logs/start",
        headers=headers,
        json={
            "shift_id": shift["id"],
            "nature_of_work": "discharging",
            "working_area": "deck_free_bay",
            "vessel_name": "MV Test",
            "bay_reference": "BAY-12",
            "container_count": 0,
            "started_at": "2026-08-21T08:15:00",
        },
    )
    assert task_response.status_code == 201
    task = task_response.json()

    delay_response = client.post(
        "/api/delay-logs/start",
        headers=headers,
        json={
            "task_log_id": task["id"],
            "delay_type": "crane_travelling",
            "started_at": "2026-08-21T08:30:00",
            "is_operator_controllable": False,
            "notes": "Crane repositioning before next container move",
        },
    )
    assert delay_response.status_code == 201
    delay = delay_response.json()

    delay_end_response = client.patch(
        f"/api/delay-logs/{delay['id']}/end",
        headers=headers,
        json={
            "ended_at": "2026-08-21T08:45:00",
            "notes": "Crane travelling completed",
        },
    )
    assert delay_end_response.status_code == 200
    assert delay_end_response.json()["duration_minutes"] == 15

    task_end_response = client.patch(
        f"/api/task-logs/{task['id']}/end",
        headers=headers,
        json={
            "ended_at": "2026-08-21T09:15:00",
            "container_count": 12,
            "notes": "Task completed",
        },
    )
    assert task_end_response.status_code == 200
    assert task_end_response.json()["status"] == "completed"

    summary_response = client.get("/api/operators/me/summary", headers=headers)
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_shifts"] == 1
    assert summary["active_shift_id"] == shift["id"]
    assert summary["completed_tasks"] == 1
    assert summary["total_container_count"] == 12
    assert summary["total_delay_minutes"] == 15

    shift_end_response = client.patch(
        f"/api/shifts/{shift['id']}/end",
        headers=headers,
        json={
            "ended_at": "2026-08-21T10:00:00",
            "notes": "Shift A completed",
        },
    )
    assert shift_end_response.status_code == 200
    assert shift_end_response.json()["status"] == "completed"


# Purpose: verify operators can only choose Shift A, Shift B, or Shift C.
def test_start_shift_rejects_invalid_shift_code(client):
    seed_crane()
    register_user(client, "operator@example.com", "operator")
    headers = login_header(client, "operator@example.com")

    response = client.post(
        "/api/shifts/start",
        headers=headers,
        json={
            "mhc_number": "MHC-01",
            "shift_code": "D",
            "started_at": "2026-08-21T08:00:00",
        },
    )

    assert response.status_code == 400


# Purpose: verify RBAC blocks managers from operator-only workflow routes.
def test_manager_cannot_start_operator_shift(client):
    seed_crane()
    register_user(client, "manager@example.com", "manager")
    headers = login_header(client, "manager@example.com")

    response = client.post(
        "/api/shifts/start",
        headers=headers,
        json={
            "mhc_number": "MHC-01",
            "shift_code": "B",
            "started_at": "2026-08-21T08:00:00",
        },
    )

    assert response.status_code == 403


# Purpose: verify a task cannot close while a delay is still active.
def test_task_cannot_end_before_active_delay_is_ended(client):
    seed_crane()
    register_user(client, "operator@example.com", "operator")
    headers = login_header(client, "operator@example.com")

    shift = client.post(
        "/api/shifts/start",
        headers=headers,
        json={
            "mhc_number": "MHC-01",
            "shift_code": "C",
            "started_at": "2026-08-21T08:00:00",
        },
    ).json()
    task = client.post(
        "/api/task-logs/start",
        headers=headers,
        json={
            "shift_id": shift["id"],
            "nature_of_work": "discharging",
            "working_area": "deck_free_bay",
            "started_at": "2026-08-21T08:15:00",
        },
    ).json()
    client.post(
        "/api/delay-logs/start",
        headers=headers,
        json={
            "task_log_id": task["id"],
            "delay_type": "awaiting_trucks",
            "started_at": "2026-08-21T08:30:00",
        },
    )

    response = client.patch(
        f"/api/task-logs/{task['id']}/end",
        headers=headers,
        json={"ended_at": "2026-08-21T09:00:00"},
    )

    assert response.status_code == 409



# Purpose: verify the operator can recover the open shift, task, and delay after a page reload.
def test_operator_active_state_follows_the_workflow(client):
    seed_crane()
    register_user(client, "operator@example.com", "operator")
    headers = login_header(client, "operator@example.com")

    def active_state():
        response = client.get("/api/operators/me/active", headers=headers)
        assert response.status_code == 200
        return response.json()

    assert active_state() == {"shift": None, "task": None, "delay": None}

    shift = client.post(
        "/api/shifts/start",
        headers=headers,
        json={"mhc_number": "MHC-01", "shift_code": "A", "started_at": "2026-08-21T08:00:00"},
    ).json()
    state = active_state()
    assert state["shift"]["id"] == shift["id"]
    assert state["task"] is None and state["delay"] is None

    task = client.post(
        "/api/task-logs/start",
        headers=headers,
        json={"shift_id": shift["id"], "nature_of_work": "discharging", "working_area": "deck_free_bay", "started_at": "2026-08-21T08:15:00"},
    ).json()
    assert active_state()["task"]["id"] == task["id"]

    delay = client.post(
        "/api/delay-logs/start",
        headers=headers,
        json={"task_log_id": task["id"], "delay_type": "awaiting_trucks", "started_at": "2026-08-21T08:30:00"},
    ).json()
    assert active_state()["delay"]["id"] == delay["id"]

    client.patch(f"/api/delay-logs/{delay['id']}/end", headers=headers, json={"ended_at": "2026-08-21T08:45:00"})
    assert active_state()["delay"] is None

    client.patch(f"/api/task-logs/{task['id']}/end", headers=headers, json={"ended_at": "2026-08-21T09:15:00"})
    assert active_state()["task"] is None

    client.patch(f"/api/shifts/{shift['id']}/end", headers=headers, json={"ended_at": "2026-08-21T10:00:00"})
    assert active_state() == {"shift": None, "task": None, "delay": None}


# Purpose: verify only operators can read the active-state route, and anonymous callers are rejected.
def test_manager_cannot_read_operator_active_state(client):
    register_user(client, "manager@example.com", "manager")
    headers = login_header(client, "manager@example.com")

    assert client.get("/api/operators/me/active", headers=headers).status_code == 403
    assert client.get("/api/operators/me/active").status_code == 401



# Purpose: verify a new shift starts at zero while the earlier shift keeps its own totals.
def test_shift_summary_is_scoped_to_each_shift(client):
    seed_crane("MHC-01")
    seed_crane("MHC-02")
    register_user(client, "operator@example.com", "operator")
    headers = login_header(client, "operator@example.com")

    first_shift = client.post(
        "/api/shifts/start",
        headers=headers,
        json={"mhc_number": "MHC-01", "shift_code": "A", "started_at": "2026-08-21T08:00:00"},
    ).json()
    task = client.post(
        "/api/task-logs/start",
        headers=headers,
        json={"shift_id": first_shift["id"], "nature_of_work": "discharging", "working_area": "deck_free_bay", "started_at": "2026-08-21T08:15:00"},
    ).json()
    delay = client.post(
        "/api/delay-logs/start",
        headers=headers,
        json={"task_log_id": task["id"], "delay_type": "awaiting_trucks", "started_at": "2026-08-21T08:30:00"},
    ).json()
    client.patch(f"/api/delay-logs/{delay['id']}/end", headers=headers, json={"ended_at": "2026-08-21T08:45:00"})
    client.patch(
        f"/api/task-logs/{task['id']}/end",
        headers=headers,
        json={"ended_at": "2026-08-21T09:15:00", "container_count": 5},
    )
    client.patch(f"/api/shifts/{first_shift['id']}/end", headers=headers, json={"ended_at": "2026-08-21T10:00:00"})

    second_shift = client.post(
        "/api/shifts/start",
        headers=headers,
        json={"mhc_number": "MHC-02", "shift_code": "B", "started_at": "2026-08-21T14:00:00"},
    ).json()

    first = client.get(f"/api/operators/me/shifts/{first_shift['id']}/summary", headers=headers).json()
    second = client.get(f"/api/operators/me/shifts/{second_shift['id']}/summary", headers=headers).json()

    assert first == {
        "shift_id": first_shift["id"],
        "mhc_number": "MHC-01",
        "completed_tasks": 1,
        "total_container_count": 5,
        "total_delay_minutes": 15,
    }
    assert second == {
        "shift_id": second_shift["id"],
        "mhc_number": "MHC-02",
        "completed_tasks": 0,
        "total_container_count": 0,
        "total_delay_minutes": 0,
    }

    # The all-time summary still counts both shifts.
    overall = client.get("/api/operators/me/summary", headers=headers).json()
    assert overall["total_shifts"] == 2
    assert overall["completed_tasks"] == 1


# Purpose: verify an operator cannot read another operator's shift summary, and others are blocked.
def test_shift_summary_is_private_to_its_operator(client):
    seed_crane("MHC-01")
    register_user(client, "owner@example.com", "operator")
    register_user(client, "other@example.com", "operator")
    register_user(client, "manager@example.com", "manager")
    owner_headers = login_header(client, "owner@example.com")
    other_headers = login_header(client, "other@example.com")
    manager_headers = login_header(client, "manager@example.com")

    shift = client.post(
        "/api/shifts/start",
        headers=owner_headers,
        json={"mhc_number": "MHC-01", "shift_code": "A", "started_at": "2026-08-21T08:00:00"},
    ).json()
    path = f"/api/operators/me/shifts/{shift['id']}/summary"

    assert client.get(path, headers=owner_headers).status_code == 200
    assert client.get(path, headers=other_headers).status_code == 404
    assert client.get(path, headers=manager_headers).status_code == 403
    assert client.get(path).status_code == 401
