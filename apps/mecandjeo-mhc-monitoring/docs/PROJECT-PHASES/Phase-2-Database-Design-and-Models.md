## Phase 2 - Database Design And Models

Status: Completed

### Purpose

Create the data foundation for tracking operators, MHC assets, shifts, tasks, delays, working conditions, performance calculations, exports, and audit events.

### Objectives

- Translate the problem statement in `Intent.md` into relational tables.
- Add SQLAlchemy models.
- Add Pydantic schemas for future API request/response contracts.
- Capture the selected MHC number when an operator starts a work session.
- Capture crane travelling as a standard delay.
- Allow custom delay labels for known local delays not yet standardized.

### Scope

Included:

- User, operator, manager, and admin profile models.
- Crane model with `mhc_number`.
- Shift model with the selected `mhc_number`.
- Task logs.
- Delay logs with `delay_type` and `custom_delay_type`.
- Working conditions.
- Performance snapshots.
- Report exports.
- Audit logs.
- Matching Pydantic schemas.

Excluded:

- Database migrations.
- CRUD route handlers.
- Authentication integration.
- Seed-data execution.
- Report calculation logic.

### Files Changed

- `app/models.py`
- `app/schemas.py`
- `docs/4. DATABASE-SCHEMA.md`
- `Roadmap.md`
- `README.md`
- `app/config.py`
- environment examples

### How It Works

The model starts from a `User`, then connects role-specific profile tables for operator, manager, and admin details.

`Crane` stores the physical MHC asset. It has both a system code and an operator-facing `mhc_number`.

`Shift` represents the operator's login/operation session. It stores `operator_id`, `crane_id`, and `mhc_number` so the actual MHC used in the operation is captured directly.

`TaskLog` stores the actual crane work. `DelayLog` stores downtime against a task, including both standard delay categories and optional custom site-specific delay text.

`PerformanceSnapshot` is reserved for calculated metrics such as total task minutes, delay minutes, effective work minutes, container count, and moves per hour.

### Security Notes

- Passwords are represented only as `password_hash`; plain passwords should never be stored.
- RBAC roles are modeled as `operator`, `manager`, and `admin`.
- Audit logging exists in the schema so sensitive actions can later be traced.
- Standard delay values are stored as strings for flexibility, but admin-controlled reference data should be introduced before production.

### Verification

Completed:

- Python syntax compilation passed for `models.py`, `schemas.py`, `config.py`, `database.py`, `main.py`, and `routes/manager.py`.
- Documentation was checked for non-ASCII characters and cleaned.
- Stale path references were re-scanned after the folder rename.
- Seed reference values were documented in `app/db/seed_data.py`.

Deferred:

- Runtime imports require dependencies such as `SQLAlchemy` and `pydantic` to be installed in the app environment.
- Database table creation will be verified when local Docker/PostgreSQL validation begins.

### Known Gaps

- No migrations yet.
- No database seed data yet.
- No API endpoints yet for creating or reading these records.

### Next Step

Phase 3 authentication and role-based access control.