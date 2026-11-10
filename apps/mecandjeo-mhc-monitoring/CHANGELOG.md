# Changelog

## 0.7.0 - Local Docker Validation

Added:

- Explicit local-only `AUTO_CREATE_SCHEMA` startup switch for Docker PostgreSQL validation.
- Docker startup connectivity check and schema initialization helper.
- PowerShell and Git Bash Docker verification instructions.
- Updated current project structure and post-Phase-10 delivery roadmap.

Changed:

- Made PostgreSQL URLs explicitly use the installed `psycopg2` driver.

Verification:

- Docker Compose configuration passed.
- `crane-app` and `crane-db` became healthy.
- `GET /health` returned `{"status":"ok"}`.
- PostgreSQL contained all 13 application tables.
- Full pytest suite passed: 29 passed.

## 0.6.0 - Reports And Exports

Added:

- Date-filtered historical performance report endpoint.
- CSV report download endpoint.
- Export metadata history endpoint.
- Task-level delay reasons in JSON and CSV report output.
- Phase 7 report workflow tests.

Changed:

- Removed the obsolete manager report placeholder in favor of `/api/reports/*` endpoints.

Verification:

- Python syntax compilation passed.
- Full pytest suite passed: 29 passed.

## 0.5.0 - Admin Workflow

Added:

- Admin user creation and focused user update/deactivation endpoints.
- Admin-only MHC crane creation, listing, update, and deactivation endpoints.
- Admin-managed reference-data endpoints for work types, working areas, delay types, and shift labels.
- `reference_data` table with category/code uniqueness and optional short keys.
- Default reference-data seed helper, including requested delay abbreviations.
- Audit log records for all Phase 6 administrative writes.
- Phase 6 admin workflow and seed idempotency tests.

Changed:

- Public registration can create only operator accounts; admins must create manager and admin accounts.
- Split ambiguous `loading_export_3_4` into `loading_export_free_bay` and `loading_export_across_heights`.

Verification:

- Python syntax compilation passed.
- Full pytest suite passed: 26 passed.

## 0.4.0 - Manager Workflow

Added:

- Manager dashboard summary endpoint.
- Live operator status endpoint.
- Active shift overview endpoint.
- Delay breakdown endpoint.
- Performance trends endpoint.
- Manager dashboard, delay analysis, and performance service helpers.
- Phase 5 manager workflow tests.

Changed:

- Manager report placeholder is now protected by manager/admin RBAC.
- Architecture and status docs now point to Phase 6 as the next phase.

Verification:

- Full pytest suite passed: 19 passed.

## 0.3.0 - Operator Workflow

Added:

- Operator summary endpoint.
- Shift start and end endpoints.
- Shift A/B/C validation.
- Task log start and end endpoints.
- Delay log start and end endpoints.
- Working-condition capture endpoint.
- Operator workflow service helpers.
- Phase 4 operator workflow tests.
- `docs/Questions-Updates.md` to track improvement suggestions.

Changed:

- Registration now enforces stronger password complexity.
- Local development docs include PowerShell and Git Bash examples.
- Tests include purpose comments for beginner readability.

Verification:

- Python syntax compilation passed.
- Full pytest suite passed: 15 passed.

## 0.2.0 - Authentication And RBAC

Added:

- Password hashing helpers.
- JWT access token helpers.
- User registration endpoint.
- User login endpoint.
- Current authenticated user endpoint.
- Reusable role guard dependencies.
- Admin-only user list and read endpoints.
- Phase 3 API tests.

Changed:

- Pinned `bcrypt==4.0.1` for compatibility with `passlib==1.7.4`.
- Replaced deprecated UTC timestamp defaults with timezone-aware UTC helpers.

Verification:

- Python syntax compilation passed.
- Phase 3 pytest suite passed: 10 passed.

## 0.1.0 - Project Scaffold And Data Model

Added:

- Project scaffold under `apps/mecandjeo-mhc-monitoring`.
- FastAPI app entry point.
- Manager route placeholders.
- Docker and Docker Compose baseline.
- SQLAlchemy data models.
- Pydantic schemas.
- MHC number tracking on cranes and shifts.
- `crane_travelling` standard delay type.
- `custom_delay_type` for local delay values.
- Seed reference value plan for work categories, working areas, and delay types.
- Beginner-friendly phase documentation.

Changed:

- Adopted project name `mecandjeo-mhc-monitoring`.

Verification:

- Python syntax compilation passed.
