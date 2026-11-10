# Project Status

## Current Phase

Phase 8 - Local Docker Validation: Completed

Docker Compose now runs the FastAPI application against PostgreSQL locally. Both
services became healthy, the API health endpoint responded successfully, and
the full application schema was confirmed in PostgreSQL.

## Latest Verification

- Python compilation: passed.
- Full API test suite: 29 passed.
- Docker Compose configuration: passed.
- Docker/PostgreSQL runtime: passed.
- Non-blocking warning: the installed FastAPI/Starlette test client warns about
  a future `httpx` compatibility change.

Current project name:

- `mecandjeo-mhc-monitoring`

Current folder:

- `apps/mecandjeo-mhc-monitoring`

## Completed

### Phase 1 - Project Scaffold

Status: Completed

Summary:

- Created FastAPI app scaffold.
- Added manager route placeholder.
- Added Docker and Docker Compose baseline.
- Added docs, tests, and infra folders.

Verification:

- Python syntax compilation passed for scaffold files.

### Phase 2 - Database Design And Models

Status: Completed

Summary:

- Added SQLAlchemy models.
- Added Pydantic schemas.
- Added MHC number tracking.
- Added standard `crane_travelling` delay.
- Added custom delay support through `custom_delay_type`.
- Documented seed reference values for nature of work, working areas, and delay types.
- Expanded database schema documentation.

Verification:

- Python syntax compilation passed for model/schema files.

### Phase 3 - Authentication And RBAC

Status: Completed

Summary:

- Added password hashing with Passlib and bcrypt.
- Added JWT access token creation and validation.
- Added registration, login, and current-user endpoints.
- Added reusable role guard dependencies.
- Added admin-only user listing and read endpoints.
- Added API tests for auth and RBAC behavior.

Verification:

- Python syntax compilation passed.
- Phase 3 pytest suite passed: 10 passed.

### Phase 4 - Operator Workflow

Status: Completed

Summary:

- Added operator summary endpoint.
- Added shift start/end endpoints.
- Added Shift A/B/C validation.
- Added task start/end endpoints.
- Added delay start/end endpoints.
- Added working-condition capture endpoint.
- Required `ended_at` for all close/end actions.
- Added stronger password validation from improvement notes.
- Added improvement-response tracking in `docs/Questions-Updates.md`.

Verification:

- Python syntax compilation passed.
- Full pytest suite passed: 15 passed.

### Phase 5 - Manager Workflow

Status: Completed

Summary:

- Replaced manager route placeholders with manager/admin-only dashboard endpoints.
- Added live operator status for active shifts.
- Added active shift overview.
- Added delay breakdown analysis by standard and custom delay type.
- Added performance trends by operator, crane, nature of work, or date.
- Added manager workflow service helpers and tests.

Verification:

- Full pytest suite passed: 19 passed.

### Phase 6 - Admin Workflow

Status: Completed

Summary:

- Added protected user create, update, password-reset, and deactivation actions.
- Added protected MHC crane create, list, update, and deactivation actions.
- Added managed reference data for work types, working areas, delay types, and shift labels.
- Added requested delay short keys and split the ambiguous loading-export work category.
- Added audit log records for every Phase 6 admin write.
- Restricted public registration to operator accounts.

Verification:

- Python syntax compilation passed.
- Full pytest suite passed: 26 passed.

### Phase 7 - Reports And Exports

Status: Completed

Summary:

- Added manager/admin historical performance reports with date, operator, crane, and work-type filters.
- Included task duration, delay duration, effective work time, container totals, moves per hour, and delay reasons.
- Added direct CSV download with per-task delay reasons.
- Stored completed export metadata in `report_exports` without persisting files on the API container.
- Added export-history access: managers see their own history, while admins see all metadata.

Verification:

- Python syntax compilation passed.
- Full pytest suite passed: 29 passed.

## In Progress

None.

## Next

Phase 9 - AWS infrastructure.

## Known Gaps

- Database migrations are pending.
- Container images and database runtime were locally validated, but AWS deployment is pending.
- GitHub push after phase completion is documented as a process item, pending explicit user approval.
