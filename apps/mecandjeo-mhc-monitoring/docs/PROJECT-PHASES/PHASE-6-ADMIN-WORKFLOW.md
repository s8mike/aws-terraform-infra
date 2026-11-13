## Phase 6 - Admin Workflow

Status: Completed

### Purpose

Give trusted administrators a controlled way to maintain users, MHC assets, and the operational lookup values used in operator workflows and reports.

### Objectives

- Create, update, reset, and deactivate user accounts.
- Create, update, list, and deactivate MHC crane assets.
- Maintain work types, working areas, delay types, and shift labels centrally.
- Record administrative changes for traceability.
- Prevent public callers from self-assigning privileged roles.

### Scope

Included:

- Admin-only user management under `/api/admin/users`.
- Admin-only reference-data management under `/api/admin/reference-data`.
- Admin-only crane management under `/api/cranes`.
- Soft deactivation through `is_active` instead of hard deletes.
- `reference_data` model and idempotent default seed helper.
- Audit log records for each administrative write.
- Phase 6 API tests.

Excluded:

- First production-admin bootstrap automation.
- Enforcing active reference values on existing operator string fields.
- CSV/PDF reporting and exports.
- PostgreSQL Docker validation and AWS deployment.

### Files Changed

- `app/models.py`
- `app/schemas.py`
- `app/main.py`
- `app/routes/auth.py`
- `app/routes/admins.py`
- `app/routes/cranes.py`
- `app/services/admin_service.py`
- `app/db/seed_data.py`
- `tests/test_admin_workflow.py`
- existing auth, operator, and manager tests for secure test account setup
- project and topic documentation

### How It Works

An admin logs in and sends a bearer token to the Phase 6 endpoints. The RBAC dependency verifies the `admin` role before any database action. User and crane records are retired with `is_active: false`, so past shifts, tasks, and reports continue to keep their original meaning.

Reference data stores a stable machine `code`, a human-friendly `label`, and an optional short key such as `AT` for awaiting trucks. The seed helper inserts the default values once and safely does nothing on later runs.

Every successful admin write creates an `audit_logs` record. The API also blocks an administrator from deactivating or demoting their own account, avoiding a simple administrative lockout.

### Security Notes

- Admin endpoints require a valid admin JWT.
- Public registration can create operators only.
- Passwords created or reset by an admin are hashed with bcrypt.
- Duplicate user emails, crane identities, and reference category/code pairs are rejected.
- No hard-delete endpoint exists for users, cranes, or reference data.
- The initial production admin must be provisioned through a controlled deployment process, documented as a remaining gap.

### Verification

PowerShell:

```powershell
.\.venv\Scripts\python.exe -m compileall app tests
.\.venv\Scripts\python.exe -m pytest tests -vv

.\.venv\Scripts\python.exe -m pytest tests\test_admin_workflow.py -vv
```

Git Bash:

```bash
./.venv/Scripts/python.exe -m compileall app tests
./.venv/Scripts/python.exe -m pytest tests -vv

./.venv/Scripts/python.exe -m pytest tests/test_admin_workflow.py -vv

```

Result:

- Python compilation passed.
- 26 total tests passed. Tests cover audit records, self-lockout prevention, reference-data seeding, and role denial. Note that test has potential to increase as other features are being added (71 passed)
- One non-blocking FastAPI/Starlette `TestClient` deprecation warning remains.

### Known Gaps

- Automated first-admin bootstrap is pending.
- Tests use SQLite; PostgreSQL validation is planned for Phase 8.
- Existing operator endpoints accept strings and do not yet require an active managed reference value.

### Next Step

Phase 7 reports and exports.