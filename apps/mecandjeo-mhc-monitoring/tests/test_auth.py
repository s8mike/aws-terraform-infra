import os

import jwt

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import User


# Helper creates a user through the public registration endpoint.
def register_user(client, email: str, role: str):
    if role != "operator":
        db = SessionLocal()
        try:
            user = User(email=email, full_name="Test User", password_hash=get_password_hash("Securepass123!"), role=role, is_active=True)
            db.add(user)
            db.commit()
        finally:
            db.close()
        return None
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
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


# Registration hashes the password and returns public user data.
def test_register_user(client):
    response = register_user(client, "operator@example.com", "operator")

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "operator@example.com"
    assert body["role"] == "operator"
    assert "password" not in body
    assert "password_hash" not in body


# Duplicate email registration is rejected to preserve unique identities.
def test_duplicate_registration_is_rejected(client):
    register_user(client, "operator@example.com", "operator")
    response = register_user(client, "operator@example.com", "operator")

    assert response.status_code == 409


# Login returns a bearer token that can be used to read /me.
def test_login_and_read_current_user(client):
    register_user(client, "manager@example.com", "manager")
    headers = login_header(client, "manager@example.com")

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "manager@example.com"


# Login token includes user identity and role claims for RBAC decisions.
def test_login_token_contains_identity_and_role_claims(client):
    register_user(client, "manager@example.com", "manager")

    response = client.post(
        "/api/auth/login",
        json={"email": "manager@example.com", "password": "Securepass123!"},
    )
    token = response.json()["access_token"]
    payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])

    assert payload["email"] == "manager@example.com"
    assert payload["role"] == "manager"
    assert payload["sub"]


# Bad credentials are rejected without issuing a token.
def test_login_rejects_bad_password(client):
    register_user(client, "operator@example.com", "operator")
    response = client.post(
        "/api/auth/login",
        json={"email": "operator@example.com", "password": "Wrongpass123!"},
    )

    assert response.status_code == 401


# Weak passwords are rejected before hashing to enforce the security policy.
def test_register_rejects_weak_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "weak@example.com",
            "full_name": "Weak Password",
            "password": "weakpass123",
            "role": "operator",
            "is_active": True,
        },
    )

    assert response.status_code == 422


# Public registration must not allow a caller to grant themselves privileged access.
def test_register_rejects_privileged_role(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "untrusted-admin@example.com",
            "full_name": "Untrusted Admin",
            "password": "Securepass123!",
            "role": "admin",
        },
    )

    assert response.status_code == 403


# Protected routes reject requests without bearer tokens.
def test_me_rejects_missing_token(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


# Protected routes reject malformed or invalid bearer tokens.
def test_me_rejects_invalid_token(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


# Admin users can access the admin-only user listing endpoint.
def test_admin_can_list_users(client):
    register_user(client, "admin@example.com", "admin")
    headers = login_header(client, "admin@example.com")

    response = client.get("/api/users/", headers=headers)

    assert response.status_code == 200
    assert response.json()[0]["email"] == "admin@example.com"


# Operator users are blocked from admin-only account listing.
def test_operator_cannot_list_users(client):
    register_user(client, "operator@example.com", "operator")
    headers = login_header(client, "operator@example.com")

    response = client.get("/api/users/", headers=headers)

    assert response.status_code == 403
