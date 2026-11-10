# Phase 7: tests for historical performance reports and CSV exports.
from app.auth import get_password_hash
import pytest
from app.database import SessionLocal
from app.models import Crane, User

pytestmark = pytest.mark.usefixtures("seeded_reference_data")


# Create a user directly for privileged test roles because public registration is operator-only.
def create_user(email: str, role: str) -> None:
    db = SessionLocal()
    try:
        db.add(User(email=email, full_name=f"{role.title()} User", password_hash=get_password_hash("Securepass123!"), role=role, is_active=True))
        db.commit()
    finally:
        db.close()


# Log in and return a bearer header for a protected report request.
def login_header(client, email: str):
    response = client.post("/api/auth/login", json={"email": email, "password": "Securepass123!"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# Set up one completed operator task with a finished delay for report calculations.
def create_completed_activity(client):
    db = SessionLocal()
    try:
        db.add(Crane(code="MHC-07", mhc_number="MHC-07", name="Mobile Harbour Crane 07", is_active=True))
        db.commit()
    finally:
        db.close()
    client.post("/api/auth/register", json={"email": "operator@example.com", "full_name": "Report Operator", "password": "Securepass123!", "role": "operator"})
    headers = login_header(client, "operator@example.com")
    shift = client.post("/api/shifts/start", headers=headers, json={"mhc_number": "MHC-07", "shift_code": "A", "started_at": "2026-09-01T08:00:00"}).json()
    task = client.post("/api/task-logs/start", headers=headers, json={"shift_id": shift["id"], "nature_of_work": "discharging", "working_area": "deck_free_bay", "vessel_name": "MV Report", "started_at": "2026-09-01T08:00:00"}).json()
    delay = client.post("/api/delay-logs/start", headers=headers, json={"task_log_id": task["id"], "delay_type": "awaiting_trucks", "started_at": "2026-09-01T08:15:00"}).json()
    client.patch(f"/api/delay-logs/{delay['id']}/end", headers=headers, json={"ended_at": "2026-09-01T08:30:00"})
    client.patch(f"/api/task-logs/{task['id']}/end", headers=headers, json={"ended_at": "2026-09-01T09:00:00", "container_count": 18})


# Purpose: verify managers receive date-filtered production and delay context in JSON.
def test_manager_can_read_historical_performance_report(client):
    create_completed_activity(client)
    create_user("manager@example.com", "manager")
    headers = login_header(client, "manager@example.com")

    response = client.get("/api/reports/performance?date_from=2026-09-01T00:00:00&date_to=2026-09-01T23:59:59", headers=headers)

    assert response.status_code == 200
    report = response.json()
    assert report["summary"] == {"completed_tasks": 1, "total_task_minutes": 60, "total_delay_minutes": 15, "effective_work_minutes": 45, "total_container_count": 18, "moves_per_hour": 24.0}
    assert report["tasks"][0]["mhc_number"] == "MHC-07"
    assert report["delay_breakdown"][0]["delay_type"] == "awaiting_trucks"


# Purpose: verify CSV downloads have report data and leave a traceable export record.
def test_manager_can_export_csv_and_view_own_export_history(client):
    create_completed_activity(client)
    create_user("manager@example.com", "manager")
    headers = login_header(client, "manager@example.com")

    export_response = client.get("/api/reports/performance.csv", headers=headers)
    history_response = client.get("/api/reports/exports", headers=headers)

    assert export_response.status_code == 200
    assert export_response.headers["content-type"].startswith("text/csv")
    assert "MHC-07" in export_response.text
    assert "awaiting_trucks" in export_response.text
    assert history_response.status_code == 200
    assert history_response.json()[0]["report_type"] == "historical_performance"
    assert history_response.json()[0]["file_format"] == "csv"


# Purpose: verify report access is restricted and invalid date periods are rejected clearly.
def test_reports_enforce_rbac_and_date_order(client):
    client.post("/api/auth/register", json={"email": "operator@example.com", "full_name": "Report Operator", "password": "Securepass123!", "role": "operator"})
    operator_headers = login_header(client, "operator@example.com")
    create_user("manager@example.com", "manager")
    manager_headers = login_header(client, "manager@example.com")

    denied_response = client.get("/api/reports/performance", headers=operator_headers)
    invalid_dates_response = client.get("/api/reports/performance?date_from=2026-09-02T00:00:00&date_to=2026-09-01T00:00:00", headers=manager_headers)

    assert denied_response.status_code == 403
    assert invalid_dates_response.status_code == 400
