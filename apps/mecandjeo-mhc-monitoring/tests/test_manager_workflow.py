# Phase 5: tests for manager dashboard, live status, and analysis workflows.
import pytest
from app.database import SessionLocal
from app.auth import get_password_hash
from app.models import Crane
from app.models import User

pytestmark = pytest.mark.usefixtures("seeded_reference_data")

# Helper creates an active MHC for operator and manager workflow tests.
def seed_crane(mhc_number: str = "MHC-05"):
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


# Helper registers a user through the public auth endpoint.
def register_user(client, email: str, role: str):
    if role != "operator":
        db = SessionLocal()
        try:
            db.add(User(email=email, full_name=f"{role.title()} User", password_hash=get_password_hash("Securepass123!"), role=role, is_active=True))
            db.commit()
        finally:
            db.close()
        return None
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "full_name": f"{role.title()} User",
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


# Helper starts an active operator shift, task, and delay for live manager views.
def create_active_operator_activity(client):
    seed_crane()
    register_user(client, "operator@example.com", "operator")
    operator_headers = login_header(client, "operator@example.com")

    shift = client.post(
        "/api/shifts/start",
        headers=operator_headers,
        json={
            "mhc_number": "MHC-05",
            "shift_code": "A",
            "started_at": "2026-08-21T08:00:00",
        },
    ).json()
    task = client.post(
        "/api/task-logs/start",
        headers=operator_headers,
        json={
            "shift_id": shift["id"],
            "nature_of_work": "discharging",
            "working_area": "deck_free_bay",
            "vessel_name": "MV Manager Test",
            "container_count": 0,
            "started_at": "2026-08-21T08:15:00",
        },
    ).json()
    delay = client.post(
        "/api/delay-logs/start",
        headers=operator_headers,
        json={
            "task_log_id": task["id"],
            "delay_type": "awaiting_trucks",
            "started_at": "2026-08-21T08:30:00",
            "is_operator_controllable": True,
        },
    ).json()

    return operator_headers, shift, task, delay


# Helper completes the active task so performance and delay analytics have data.
def complete_operator_activity(client, operator_headers, task, delay):
    client.patch(
        f"/api/delay-logs/{delay['id']}/end",
        headers=operator_headers,
        json={"ended_at": "2026-08-21T08:50:00"},
    )
    return client.patch(
        f"/api/task-logs/{task['id']}/end",
        headers=operator_headers,
        json={
            "ended_at": "2026-08-21T09:15:00",
            "container_count": 24,
        },
    ).json()


# Purpose: verify managers can see active operator, task, crane, and delay status.
def test_manager_can_view_live_operator_status_and_dashboard(client):
    create_active_operator_activity(client)
    register_user(client, "manager@example.com", "manager")
    manager_headers = login_header(client, "manager@example.com")

    dashboard_response = client.get("/api/manager/dashboard", headers=manager_headers)
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["total_operators"] == 1
    assert dashboard["total_cranes"] == 1
    assert dashboard["active_shifts"] == 1
    assert dashboard["active_tasks"] == 1
    assert dashboard["active_delays"] == 1

    live_response = client.get(
        "/api/manager/operators/live-status",
        headers=manager_headers,
    )
    assert live_response.status_code == 200
    live_status = live_response.json()[0]
    assert live_status["mhc_number"] == "MHC-05"
    assert live_status["shift_code"] == "A"
    assert live_status["active_delay_type"] == "awaiting_trucks"
    assert live_status["status"] == "delayed"


# Purpose: verify managers can review completed task trends and delay breakdowns.
def test_manager_can_view_performance_trends_and_delay_breakdown(client):
    operator_headers, shift, task, delay = create_active_operator_activity(client)
    complete_operator_activity(client, operator_headers, task, delay)
    register_user(client, "manager@example.com", "manager")
    manager_headers = login_header(client, "manager@example.com")

    active_shifts_response = client.get(
        "/api/manager/shifts/active",
        headers=manager_headers,
    )
    assert active_shifts_response.status_code == 200
    active_shift = active_shifts_response.json()[0]
    assert active_shift["shift_id"] == shift["id"]
    assert active_shift["completed_task_count"] == 1
    assert active_shift["total_container_count"] == 24

    breakdown_response = client.get(
        "/api/manager/delays/breakdown",
        headers=manager_headers,
    )
    assert breakdown_response.status_code == 200
    breakdown = breakdown_response.json()[0]
    assert breakdown["delay_type"] == "awaiting_trucks"
    assert breakdown["delay_count"] == 1
    assert breakdown["total_delay_minutes"] == 20
    assert breakdown["operator_controllable_count"] == 1

    trends_response = client.get(
        "/api/manager/performance/trends?group_by=operator",
        headers=manager_headers,
    )
    assert trends_response.status_code == 200
    trend = trends_response.json()[0]
    assert trend["completed_tasks"] == 1
    assert trend["total_task_minutes"] == 60
    assert trend["total_delay_minutes"] == 20
    assert trend["effective_work_minutes"] == 40
    assert trend["total_container_count"] == 24
    assert trend["moves_per_hour"] == 36.0


# Purpose: verify operator users cannot read manager-only dashboard endpoints.
def test_operator_cannot_view_manager_dashboard(client):
    create_active_operator_activity(client)
    operator_headers = login_header(client, "operator@example.com")

    response = client.get("/api/manager/dashboard", headers=operator_headers)

    assert response.status_code == 403


# Purpose: verify invalid performance grouping values are rejected clearly.
def test_manager_performance_trends_reject_invalid_group_by(client):
    create_active_operator_activity(client)
    register_user(client, "manager@example.com", "manager")
    manager_headers = login_header(client, "manager@example.com")

    response = client.get(
        "/api/manager/performance/trends?group_by=invalid",
        headers=manager_headers,
    )

    assert response.status_code == 400
