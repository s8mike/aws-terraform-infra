# Phase 9: tests for the read-only lookup endpoint used by operator, manager, and admin forms.
import pytest

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import Crane, ReferenceData, User

pytestmark = pytest.mark.usefixtures("seeded_reference_data")

PASSWORD = "Securepass123!"


# Create a test account directly so every role can be tested.
def create_user(email: str, role: str) -> None:
    db = SessionLocal()
    try:
        db.add(User(email=email, full_name=f"{role.title()} User", password_hash=get_password_hash(PASSWORD), role=role, is_active=True))
        db.commit()
    finally:
        db.close()


# Log in and return a bearer header for protected endpoint requests.
def login_header(client, email: str):
    response = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# Add a crane directly, active or inactive.
def add_crane(mhc_number: str, is_active: bool = True) -> None:
    db = SessionLocal()
    try:
        db.add(Crane(code=mhc_number, mhc_number=mhc_number, name=f"Mobile Harbour Crane {mhc_number}", is_active=is_active))
        db.commit()
    finally:
        db.close()


# Retire one reference value the way an admin would.
def deactivate_reference(category: str, code: str) -> None:
    db = SessionLocal()
    try:
        row = db.query(ReferenceData).filter_by(category=category, code=code).one()
        row.is_active = False
        db.commit()
    finally:
        db.close()


# Purpose: verify every authenticated role can read the seeded lookup values.
@pytest.mark.parametrize("role", ["operator", "manager", "admin"])
def test_lookups_available_to_every_role(client, role):
    create_user(f"{role}@example.com", role)
    headers = login_header(client, f"{role}@example.com")

    response = client.get("/api/lookups", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body["nature_of_work"]) == 5
    assert len(body["working_area"]) == 8
    assert len(body["delay_type"]) == 12
    assert [item["code"] for item in body["shift_code"]] == ["A", "B", "C"]
    assert body["cranes"] == []


# Purpose: verify anonymous callers are rejected.
def test_lookups_require_authentication(client):
    assert client.get("/api/lookups").status_code == 401


# Purpose: verify a forged or malformed token is rejected.
def test_lookups_reject_invalid_token(client):
    response = client.get("/api/lookups", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


# Purpose: verify retired reference values and inactive cranes never reach operator forms.
def test_lookups_hide_inactive_values_and_cranes(client):
    create_user("operator@example.com", "operator")
    add_crane("MHC-01")
    add_crane("MHC-02", is_active=False)
    deactivate_reference("delay_type", "breakdown")
    headers = login_header(client, "operator@example.com")

    body = client.get("/api/lookups", headers=headers).json()

    delay_codes = [item["code"] for item in body["delay_type"]]
    assert "breakdown" not in delay_codes
    assert len(delay_codes) == 11
    assert [crane["mhc_number"] for crane in body["cranes"]] == ["MHC-01"]