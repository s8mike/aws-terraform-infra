# mecandjeo-mhc-monitoring Roadmap

This roadmap guides the end-to-end execution of the Mobile Harbour Crane Operator Performance Monitoring System. The project follows the same general application format as `mecandjeo-school`, but the domain is port operations, crane activity logging, delay analysis, operator performance, and manager reporting.

## Project Goal

Build a FastAPI and PostgreSQL application that allows crane operators to log work, working conditions, and delays, while managers and admins get real-time visibility into performance trends, bottlenecks, and operational reports.

## Problem Summary

Mobile harbour crane operator performance is hard to assess fairly because task completion time is affected by conditions outside the operator's control, including container availability, truck availability, clerks, stevedores, control room changes, wrong instructions, equipment breakdowns, vessel command instructions, and weather.

The system must capture those operational realities so performance can be measured with context instead of raw speed alone.

## Target Users

- Operator: logs shifts, tasks, working areas, working conditions, delays, and views personal performance.
- Manager: monitors live operator status, reviews performance trends, analyzes delays, and exports reports.
- Admin: manages users, cranes, roles, work types, delay types, and system settings.

## Technology Direction

- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Schemas: Pydantic
- Authentication: JWT with role-based access control
- Local runtime: Docker Compose
- Cloud runtime: AWS ECS, ALB, CloudWatch, and PostgreSQL/RDS
- Infrastructure: Terraform, reusing the existing shared AWS infrastructure in this repo

## Application Structure

```text
apps/mecandjeo-mhc-monitoring/
|-- app/
|   |-- auth.py, config.py, database.py, logger.py, main.py, models.py, schemas.py
|   |-- db/
|   |   `-- seed_data.py
|   |-- routes/
|   |   |-- admins.py, auth.py, cranes.py, delay_logs.py, manager.py
|   |   |-- operators.py, reports.py, shifts.py, task_logs.py, users.py
|   |   `-- working_conditions.py
|   `-- services/
|       |-- admin_service.py, dashboard_service.py, delay_analysis_service.py
|       |-- operator_service.py, performance_service.py
|       `-- report_service.py
|-- docs/
|   |-- API-DESIGN.md, DATABASE-SCHEMA.md, LOCAL-DEVELOPMENT.md
|   |-- PROJECT-PHASES.md, Questions-Improvements.md, Questions-Updates.md
|   |-- REPORTING-DASHBOARD.md, SECURITY-RBAC.md
|-- infra/
|   |-- dev/ (Terraform environment configuration)
|   `-- modules/rds-postgres/ (reusable database module)
|-- tests/
|   |-- conftest.py
|   |-- test_admin_workflow.py, test_auth.py, test_health.py
|   |-- test_manager_workflow.py, test_operator_workflow.py
|   `-- test_reports.py
|-- .env.example, .env.docker.example, .gitignore, .dockerignore
|-- Dockerfile, Dockerfile.multistage, docker-compose.yml, requirements.txt
`-- ARCHITECTURE.md, CHANGELOG.md, CONTRIBUTING.md, Intent.md, PROJECT-STATUS.md, README.md, Roadmap.md
```

## Core Database Tables

- users
- operator_profiles
- manager_profiles
- admin_profiles
- cranes
- shifts
- task_logs
- delay_logs
- working_conditions
- performance_snapshots
- report_exports
- audit_logs

## Domain Reference Data

### Nature Of Work

- across_heights_portside
- deck_free_bay
- underdeck_free_bay
- underdeck_across_heights
- loading_export_free_bay
- loading_export_across_heights
- loading_empty_single
- loading_empty_twin
- discharge_oog
- tight_space_cranes

### Working Areas

- port_side
- deck
- underdeck
- tight_space (between MHCs)
- other

### Delay Types

- awaiting_containers_empty
- awaiting_containers_export
- awaiting_trucks
- awaiting_clerks
- awaiting_stevedores
- control_room_modification
- wrong_instructions
- breakdown
- rainfall
- vessel_command_instructions
- crane_travelling
- other_delay

Known local delay values that are not yet standardized can be captured through `custom_delay_type` on delay logs.

## Phase 1 - Project Scaffold

Status: Completed

Objectives:

- Create the project structure under `apps/mecandjeo-mhc-monitoring`.
- Add FastAPI entrypoint.
- Add Docker and Docker Compose baseline.
- Add documentation placeholders.
- Add Terraform placeholders for AWS deployment.
- Add `app/routes/manager.py`.

Deliverables:

- `app/main.py`
- `app/config.py`
- `app/database.py`
- `app/routes/manager.py`
- Docker files
- docs folder
- infra folder
- tests folder

Acceptance Checks:

- Python files compile.
- `/health` route exists.
- Manager route module exists.

## Phase 2 - Database Design And Models

Status: Completed

Objectives:

- Convert the intent document into PostgreSQL-backed SQLAlchemy models.
- Add relationships between users, profiles, cranes, shifts, task logs, delays, and performance records.
- Capture the MHC number selected by the operator when starting an operation session.
- Support standard delay types and optional custom delay labels for known local delay causes.
- Define Pydantic schemas for create/read/update API contracts.

Deliverables:

- `app/models.py`
- `app/schemas.py`
- updated `docs/DATABASE-SCHEMA.md`
- seed data plan in `app/db/seed_data.py`

Acceptance Checks:

- Model and schema files compile.
- Table relationships are clear.
- Schemas match the planned API payloads.
- Python syntax compilation passes.
- Runtime import validation is deferred until project dependencies are installed in the local app environment or Docker image.

## Phase 3 - Authentication And RBAC

Status: Completed

Objectives:

- Implement user registration and login.
- Add JWT token creation and validation.
- Add role-based access for operator, manager, and admin.

Deliverables:

- `app/auth.py`
- `app/routes/auth.py`
- `app/routes/users.py`
- RBAC helper functions
- `tests/conftest.py`
- `tests/test_auth.py`

Acceptance Checks:

- Users can register and login.
- JWT tokens include role claims.
- Protected routes reject missing or invalid tokens.
- Role-specific routes reject unauthorized roles.
- Phase 3 tests pass with 10 passed.

## Phase 4 - Operator Workflow

Status: Completed

Objectives:

- Allow operators to start and end shifts.
- Allow task logging with nature of work, working area, crane, vessel, and timestamps.
- Allow delay logging with delay type, duration, and notes.
- Allow working condition capture.
- Validate operator-selected shift codes as A, B, or C.
- Require `ended_at` when closing shifts, task logs, and delay logs.

Deliverables:

- `app/routes/operators.py`
- `app/routes/shifts.py`
- `app/routes/task_logs.py`
- `app/routes/delay_logs.py`
- `app/routes/working_conditions.py`
- `app/services/operator_service.py`
- `tests/test_operator_workflow.py`

Acceptance Checks:

- Operator can create a shift.
- Operator can log a task.
- Operator can attach one or more delays to a task.
- Operator can view personal performance summary.
- Operator can record working conditions.
- Invalid shift codes are rejected.
- Manager users are blocked from operator-only routes.
- Active delays must end before their task can close.
- Phase 4 test suite passes with 15 total tests.

## Phase 5 - Manager Workflow

Status: Completed

Objectives:

- Expand `app/routes/manager.py`.
- Add live operator status.
- Add active shift overview.
- Add delay breakdowns.
- Add performance trends by operator, crane, work type, and date range.

Deliverables:

- full `app/routes/manager.py`
- `app/services/dashboard_service.py`
- `app/services/performance_service.py`
- `app/services/delay_analysis_service.py`
- manager response schemas
- `tests/test_manager_workflow.py`

Acceptance Checks:

- Manager can view active operators.
- Manager can see delay totals by category.
- Manager can compare performance across operators and cranes.
- Manager and admin users can access manager dashboard routes.
- Operator users are blocked from manager-only routes.
- Invalid performance grouping values are rejected.
- Phase 5 test suite passes with 19 total tests.

## Phase 6 - Admin Workflow

Status: Completed

Objectives:

- Add admin user management.
- Add crane management.
- Add reference data management for work types, working areas, and delay types.

Deliverables:

- `app/routes/admins.py`
- `app/routes/cranes.py`
- `app/services/admin_service.py`
- `ReferenceData` database model and default reference-data seed helper
- admin endpoints for users and reference data

Acceptance Checks:

- Admin can create/update/deactivate users.
- Admin can create/update/deactivate cranes.
- Admin can manage reference data.
- Public registration cannot grant a caller a manager or admin role.
- Admin changes are recorded in the audit log.

## Phase 7 - Reports And Exports

Status: Completed

Objectives:

- Add report endpoints for historical performance.
- Add CSV export.
- Prepare PDF report design.
- Store report export metadata.

Deliverables:

- `app/routes/reports.py`
- `app/services/report_service.py`
- updated `docs/REPORTING-DASHBOARD.md`
- `tests/test_reports.py`

Acceptance Checks:

- Manager can request date-filtered reports.
- Reports include task time, delay time, effective work time, and delay reason breakdown.
- CSV export works.
- Export metadata is stored without writing report files to the API container.

## Phase 8 - Local Docker Validation

Status: Completed

Objectives:

- Run the API and PostgreSQL locally with Docker Compose.
- Validate the app connects to PostgreSQL.
- Add test coverage for health, auth, task logs, delay logs, and performance.

Deliverables:

- working `docker-compose.yml`
- test suite under `tests/`
- updated `docs/LOCAL-DEVELOPMENT.md`

Acceptance Checks:

- `docker compose up --build` starts app and database.
- `/health` returns `{"status": "ok"}`.
- Tests pass locally.
- Docker app and database services become healthy.
- PostgreSQL creates all application tables through the local development schema switch.


## Phase 9 - Local Readiness (Backend)

Status: Completed

### Purpose

Make the application usable on a fresh local database before any frontend or cloud work. Before this phase, a clean database had no admin, no cranes, and no way for an operator to read the reference values needed by a form, so no shift could be started.

### Objectives

- Create the first admin account from settings, safely and repeatably.
- Load sample cranes for local demonstrations only.
- Give operators, managers, and admins read-only access to the approved lookup values.
- Require operator task and delay input to match active, admin-managed reference data.
- Make Swagger's Authorize button work with the JSON login endpoint.
- Document the full local setup so a beginner can follow it.


### Next Step

Phase 10: build the React and TypeScript frontend against the working local API (login, operator, manager, and admin screens).

---

## Roadmap Renumbering

Because local readiness, the frontend, and full-stack validation now come before any cloud work, replace the old Phase 9 to Phase 17 numbering with this table.

| Phase | Name | Source |
|---|---|---|
| 9 | Local readiness (backend) | New, completed |
| 10 | Frontend UI (React and TypeScript) | Old 11 |
| 11 | Full-stack local validation (frontend container, migrations, browser smoke test) | New, plus part of old 12 |
| 12 | AWS infrastructure | Old 9 |
| 13 | End-to-end deployment | Old 10 |
| 14 | Frontend CI/CD with GitHub Actions | Old 12, remainder |
| 15 | Kubernetes foundations | Old 13 |
| 16 | Helm packaging | Old 14 |
| 17 | Argo CD GitOps | Old 15 |
| 18 | Observability and reliability | Old 16 |
| 19 | Demonstration readiness | Old 17 |

Also replace **Immediate Next Step** with:

```markdown
## Immediate Next Step

Begin Phase 10 (frontend UI) against the local API. AWS work starts only after Phase 11 passes locally.
```

Update the Phase 10 and Phase 13 acceptance checks so the operator, manager, and admin flows are verified through the user interface.





==================================================================================
## Phase 12 - AWS Infrastructure

Status: Not started

Objectives:

- Reuse existing shared AWS infrastructure from this repo.
- Add crane app ECS service.
- Add ALB target group and health check.
- Add CloudWatch logs.
- Add PostgreSQL/RDS infrastructure or a clearly documented database connection strategy.

Deliverables:

- `infra/dev/main.tf`
- `infra/dev/variables.tf`
- `infra/dev/outputs.tf`
- `infra/dev/backend.tf`
- `infra/modules/rds-postgres/`
- updated `docs/AWS-DEPLOYMENT.md`

Acceptance Checks:

- Terraform validates.
- App reads shared VPC/subnet/security outputs.
- ECS task definition has required app environment variables.
- Database connection is documented and secure.

## Phase 13 - End-To-End Deployment

Status: Not started

Objectives:

- Build container image.
- Push image to ECR.
- Apply Terraform.
- Validate ECS service health.
- Validate API through ALB.
- Document post-deployment checks.

Deliverables:

- deployed ECS service
- working ALB endpoint
- CloudWatch logs
- post-deployment validation notes

Acceptance Checks:

- App is reachable from ALB.
- `/health` passes.
- Authentication works.
- Operator, manager, and admin flows work end to end.

## Execution Order

1. Complete Phase 1 scaffold verification.
2. Implement Phase 2 database models and schemas.
3. Implement Phase 3 authentication and RBAC.
4. Implement Phase 4 operator workflows.
5. Implement Phase 5 manager dashboard workflows.
6. Implement Phase 6 admin workflows.
7. Implement Phase 7 reports.
8. Validate locally with Docker in Phase 8.
9. Add AWS infrastructure in Phase 9.
10. Deploy and verify in Phase 10.

## Immediate Next Step

Begin Phase 9 by integrating the application with the existing AWS infrastructure.

## Post-Phase-10 Delivery And DevOps Roadmap

After the backend is deployed, the application will continue through the following learning-focused phases:

11. Frontend UI/UX: build a responsive React and TypeScript interface for operators, managers, and admins; prepare realistic demonstration data and presentation flows.
12. Frontend delivery: add frontend containerization, API integration, browser tests, and GitHub Actions CI/CD.
13. Kubernetes foundations: package the API, frontend, and PostgreSQL connection configuration for a local Kubernetes cluster; introduce Kubernetes manifests, health probes, secrets, and configuration.
14. Helm packaging: turn the Kubernetes resources into reusable Helm charts for development, staging, and production values.
15. Argo CD GitOps: use a dedicated environment repository or folder strategy, connect Argo CD, and promote versioned images through reviewed Git commits.
16. Observability and reliability: add CloudWatch/Prometheus-compatible metrics, dashboards, alerts, backup/restore drills, and security scanning.
17. Demonstration readiness: create guided user scenarios, sample accounts, screenshots, architecture diagrams, and a presentation script for potential subscribers.

Each post-Phase-10 phase will retain the same discipline: purpose, objectives, security notes, tests, verification, documentation, and an explicit approval before any upstream push.
