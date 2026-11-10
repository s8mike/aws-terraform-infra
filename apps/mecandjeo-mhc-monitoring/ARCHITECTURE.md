# Architecture

`mecandjeo-mhc-monitoring` is a FastAPI and PostgreSQL application for port operations performance tracking.

## High-Level Components

- FastAPI backend: serves API endpoints.
- PostgreSQL database: stores users, cranes, shifts, tasks, delays, conditions, reports, and audit events.
- SQLAlchemy: maps Python classes to database tables.
- Pydantic: validates request and response payloads.
- Docker Compose: planned local app plus database runtime.
- AWS ECS and ALB: planned cloud runtime using existing shared infrastructure.

## Current State

Completed:

- Phase 1 scaffold.
- Phase 2 data model and schemas.
- Phase 3 authentication and RBAC.
- Phase 4 operator workflow.
- Phase 5 manager workflow.
- Phase 6 admin workflow.
- Phase 7 reports and exports.
- Phase 8 local Docker and PostgreSQL validation.

Next:

- Phase 9 AWS infrastructure.

## Request Flow

Current API flow:

1. Client sends API request.
2. FastAPI route validates input with Pydantic.
3. Auth dependency checks JWT and role when required.
4. Route uses SQLAlchemy database session.
5. Data is written to or read from PostgreSQL.
6. Response is returned as JSON.

Implemented route groups:

- Auth routes handle registration, login, and current-user lookup.
- User routes expose admin-only user reads.
- Operator routes handle operator summaries.
- Shift routes handle operator shift start and end actions.
- Task log routes handle operator task start and end actions.
- Delay log routes handle operator delay start and end actions.
- Working condition routes capture operational context during a shift.
- Manager routes expose read-only dashboard, live status, delay, and performance views.
- Admin routes manage user accounts and operational reference values with audit records.
- Crane routes manage MHC assets, including soft deactivation for historical accuracy.
- Report routes provide date-filtered historical performance data, CSV downloads, and export metadata.

## Security Direction

- Secrets remain environment-based.
- Passwords are stored only as hashes.
- JWT authentication protects user identity.
- RBAC protects operator, manager, and admin workflows.
- Audit logs capture important changes.
- Public registration is limited to operator accounts; admins create privileged accounts.
