# Phase 10: tests for the self-service change-password endpoint.
import pytest

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import AuditLog, User

OLD_PASSWORD = "Securepass123!"
NEW_PASSWORD = "Brandnew456#"
URL = "/api/auth/change-password"


# Create an active account directly so every role can be tested.
def create_user(email: str, role: str = "operator") -> None:
    db = SessionLocal()
    try:
        db.add(User(email=email, full_name=f"{role.title()} User", password_hash=get_password_hash(OLD_PASSWORD), role=role, is_active=True))
        db.commit()
    finally:
        db.close()


# Log in and return the raw response, so tests can check both success and failure.
def login(client, email: str, password: str):
    return client.post("/api/auth/login", json={"email": email, "password": password})


# Log in with the original password and return a bearer header.
def auth_header(client, email: str):
    return {"Authorization": f"Bearer {login(client, email, OLD_PASSWORD).json()['access_token']}"}


# Purpose: verify every role can change its own password and then sign in with the new one.
@pytest.mark.parametrize("role", ["operator", "manager", "admin"])
def test_change_password_works_for_every_role(client, role):
    create_user(f"{role}@example.com", role)
    headers = auth_header(client, f"{role}@example.com")

    response = client.post(URL, headers=headers, json={"current_password": OLD_PASSWORD, "new_password": NEW_PASSWORD})

    assert response.status_code == 204
    assert login(client, f"{role}@example.com", NEW_PASSWORD).status_code == 200


# Purpose: verify the old password stops working once the password is changed.
def test_old_password_stops_working_and_new_one_works(client):
    create_user("operator@example.com")
    headers = auth_header(client, "operator@example.com")

    client.post(URL, headers=headers, json={"current_password": OLD_PASSWORD, "new_password": NEW_PASSWORD})

    assert login(client, "operator@example.com", OLD_PASSWORD).status_code == 401
    assert login(client, "operator@example.com", NEW_PASSWORD).status_code == 200


# Purpose: verify a wrong current password is a 400 (so the user stays signed in) and changes nothing.
def test_wrong_current_password_is_rejected_without_changes(client):
    create_user("operator@example.com")
    headers = auth_header(client, "operator@example.com")

    response = client.post(URL, headers=headers, json={"current_password": "WrongPass999!", "new_password": NEW_PASSWORD})

    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect"
    assert login(client, "operator@example.com", OLD_PASSWORD).status_code == 200


# Purpose: verify weak new passwords are rejected by the same policy used for registration.
def test_weak_new_password_is_rejected(client):
    create_user("operator@example.com")
    headers = auth_header(client, "operator@example.com")

    no_uppercase = client.post(URL, headers=headers, json={"current_password": OLD_PASSWORD, "new_password": "alllowercase1!"})
    too_short = client.post(URL, headers=headers, json={"current_password": OLD_PASSWORD, "new_password": "Ab1!"})

    assert no_uppercase.status_code == 422
    assert too_short.status_code == 422
    assert login(client, "operator@example.com", OLD_PASSWORD).status_code == 200


# Purpose: verify "changing" to the same password is refused.
def test_new_password_must_differ(client):
    create_user("operator@example.com")
    headers = auth_header(client, "operator@example.com")

    response = client.post(URL, headers=headers, json={"current_password": OLD_PASSWORD, "new_password": OLD_PASSWORD})

    assert response.status_code == 400


# Purpose: verify anonymous callers cannot reach the endpoint.
def test_change_password_requires_authentication(client):
    response = client.post(URL, json={"current_password": OLD_PASSWORD, "new_password": NEW_PASSWORD})

    assert response.status_code == 401


# Purpose: verify the change is audited, and that neither password appears in the audit trail.
def test_change_password_is_audited_without_secrets(client):
    create_user("operator@example.com")
    headers = auth_header(client, "operator@example.com")
    client.post(URL, headers=headers, json={"current_password": OLD_PASSWORD, "new_password": NEW_PASSWORD})

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "operator@example.com").one()
        entries = db.query(AuditLog).filter(AuditLog.action == "user.password_changed").all()
        assert len(entries) == 1
        assert entries[0].actor_id == user.id
        assert entries[0].entity_id == user.id
        assert OLD_PASSWORD not in (entries[0].description or "")
        assert NEW_PASSWORD not in (entries[0].description or "")
    finally:
        db.close()