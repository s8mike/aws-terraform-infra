## Phase 3 - Authentication And RBAC

Status: Completed

### Purpose

Secure the system so operators, managers, and admins can only access the workflows intended for their roles.

### Objectives

- Password hashing.
- User registration.
- Login with JWT.
- Current-user dependency.
- Role guard dependencies.
- Protected route examples.
- Documentation and tests for auth success/failure cases.

### Scope

Included:

- Registration endpoint.
- Login endpoint.
- Current-user endpoint.
- JWT encode/decode helpers.
- Password hashing and verification helpers.
- Role constants for operator, manager, and admin.
- Role guard dependency factory.
- Admin-only user inspection routes.
- Auth/RBAC tests.

Excluded:

- Refresh tokens.
- Password reset.
- Rate limiting.
- Account lockout.
- Production secret manager integration.

### Files Changed

- `app/auth.py`
- `app/routes/auth.py`
- `app/routes/users.py`
- `app/main.py`
- `app/models.py`
- `requirements.txt`
- `tests/conftest.py`
- `tests/test_auth.py`
- `tests/test_health.py`
- `docs/3. API-DESIGN.md`
- `docs/5. SECURITY-RBAC.md`
- `docs/1. LOCAL-DEVELOPMENT.md`
- `PROJECT-STATUS.md`
- `CHANGELOG.md`
- `Roadmap.md`

### How It Works

`app/auth.py` hashes passwords with Passlib and bcrypt, creates JWT access tokens with PyJWT, decodes bearer tokens, resolves the current active user, and provides reusable role guards.

`app/routes/auth.py` lets users register, login, and read their own authenticated profile.

`app/routes/users.py` exposes user inspection endpoints, but only to admins.

`app/main.py` wires the auth and user routers into the API.

### Security Notes

- Plain passwords are never returned in API responses.
- Stored passwords use `password_hash`.
- Login returns a bearer token instead of a server-side session.
- `SECRET_KEY` must come from environment configuration.
- Admin-only routes use `require_roles("admin")`.
- `bcrypt==4.0.1` is pinned because `passlib==1.7.4` is not compatible with `bcrypt==5.0.0`.
- Test secrets are at least 32 characters to avoid weak HMAC key warnings.

### Verification

Completed:

- Python syntax compilation passed.
- Local virtual environment was created under `.venv`.
- Dependencies were installed into `.venv`.
- Phase 3 pytest suite passed.

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -vv
```

Git Bash: `./.venv/Scripts/python.exe -m pytest tests/test_auth.py tests/test_health.py -vv`


Result:

- 10 tests passed at phase completion. Tests cover password rules, registration, login, JWT claims, token failure, and RBAC denial.

Remaining warning:

- FastAPI/Starlette emits a deprecation warning about `TestClient` and future `httpx` usage. This does not fail the suite.

### Known Gaps

- Tests use SQLite for fast local verification.
- PostgreSQL validation is deferred to the Docker/local database phase.
- Refresh tokens and password reset are not implemented yet.

### Next Step

Phase 4 operator workflow.
