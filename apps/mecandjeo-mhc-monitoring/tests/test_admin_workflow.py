# Phase 6: tests for secure admin user, crane, and reference-data workflows.
from app.auth import get_password_hash
from app.database import SessionLocal
from app.db.seed_data import seed_reference_data
from app.models import AuditLog, User


# Create a privileged test account directly because public registration is operator-only.
def create_user(email: str, role: str) -> None:
    db = SessionLocal()
    try:
        db.add(User(email=email, full_name=f"{role.title()} User", password_hash=get_password_hash("Securepass123!"), role=role, is_active=True))
        db.commit()
    finally:
        db.close()


# Log in and return a bearer header for protected endpoint requests.
def login_header(client, email: str):
    response = client.post("/api/auth/login", json={"email": email, "password": "Securepass123!"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# Purpose: verify an admin can create, edit, and deactivate a managed user with audit history.
def test_admin_can_manage_users_and_audit_changes(client):
    create_user("admin@example.com", "admin")
    headers = login_header(client, "admin@example.com")

    create_response = client.post("/api/admin/users", headers=headers, json={"email": "manager@example.com", "full_name": "Port Manager", "password": "Securepass123!", "role": "manager"})
    assert create_response.status_code == 201
    manager = create_response.json()
    assert manager["role"] == "manager"

    update_response = client.patch(f"/api/admin/users/{manager['id']}", headers=headers, json={"is_active": False, "full_name": "Inactive Manager"})
    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False

    db = SessionLocal()
    try:
        assert db.query(AuditLog).count() == 2
    finally:
        db.close()


# Purpose: verify an admin cannot accidentally lock themselves out of administration.
def test_admin_cannot_deactivate_or_demote_self(client):
    create_user("admin@example.com", "admin")
    headers = login_header(client, "admin@example.com")
    db = SessionLocal()
    try:
        admin_id = db.query(User).filter(User.email == "admin@example.com").one().id
    finally:
        db.close()

    deactivate = client.patch(f"/api/admin/users/{admin_id}", headers=headers, json={"is_active": False})
    demote = client.patch(f"/api/admin/users/{admin_id}", headers=headers, json={"role": "operator"})

    assert deactivate.status_code == 400
    assert demote.status_code == 400


# Purpose: verify admins can add, amend, and retire a crane without deleting work history.
def test_admin_can_manage_cranes(client):
    create_user("admin@example.com", "admin")
    headers = login_header(client, "admin@example.com")

    create_response = client.post("/api/cranes/", headers=headers, json={"code": "MHC-06", "mhc_number": "MHC-06", "name": "Mobile Harbour Crane 06", "capacity_tonnes": 125})
    assert create_response.status_code == 201
    crane = create_response.json()

    update_response = client.patch(f"/api/cranes/{crane['id']}", headers=headers, json={"location": "Berth 4", "is_active": False})
    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False
    assert update_response.json()["location"] == "Berth 4"


# Purpose: verify admins can manage keyed delay and work reference values for future forms.
def test_admin_can_manage_reference_data(client):
    create_user("admin@example.com", "admin")
    headers = login_header(client, "admin@example.com")

    create_response = client.post("/api/admin/reference-data", headers=headers, json={"category": "delay_type", "code": "awaiting_containers", "label": "Awaiting Containers", "short_key": "ACon"})
    assert create_response.status_code == 201
    reference_data = create_response.json()
    assert reference_data["short_key"] == "ACon"

    update_response = client.patch(f"/api/admin/reference-data/{reference_data['id']}", headers=headers, json={"is_active": False})
    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False

    list_response = client.get("/api/admin/reference-data?category=delay_type", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()[0]["code"] == "awaiting_containers"


# Purpose: verify managers cannot alter users, cranes, or operational reference values.
def test_non_admin_is_blocked_from_admin_management(client):
    create_user("manager@example.com", "manager")
    headers = login_header(client, "manager@example.com")

    user_response = client.post("/api/admin/users", headers=headers, json={"email": "operator@example.com", "full_name": "Operator", "password": "Securepass123!", "role": "operator"})
    crane_response = client.get("/api/cranes/", headers=headers)
    reference_response = client.get("/api/admin/reference-data", headers=headers)

    assert user_response.status_code == 403
    assert crane_response.status_code == 403
    assert reference_response.status_code == 403


# Purpose: verify default managed operational values can seed once without duplication.
def test_reference_data_seed_is_idempotent(client):
    db = SessionLocal()
    try:
        first_created = seed_reference_data(db)
        second_created = seed_reference_data(db)
    finally:
        db.close()

    assert first_created > 0
    assert second_created == 0
