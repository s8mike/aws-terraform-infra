# Project Phases

This document is the beginner-friendly execution log for `mecandjeo-mhc-monitoring`. Each phase should explain why the phase exists, what changed, how to verify it, and whether it is safe to move to the next phase.

## Phase Documentation Standard

Every completed phase should include:

- Purpose: why the phase matters.
- Objectives: what the phase is expected to achieve.
- Scope: what is included and intentionally excluded.
- Files changed: important files created or updated.
- How it works: short explanation for beginners.
- Security notes: risks and controls introduced by the phase.
- Verification: commands/checks run and results.
- Known gaps: what remains incomplete or deferred.
- Next step: the next recommended phase.

## Phase 1 - Project Scaffold

Status: Completed

### Purpose

Create a clean project foundation that follows the same broad application shape as `mecandjeo-school`, while giving the MHC monitoring system its own self-contained folder.

### Objectives

- Create the app folder under `apps/mecandjeo-mhc-monitoring`.
- Add the FastAPI entry point.
- Add basic configuration and database wiring files.
- Add a manager route placeholder.
- Add Docker and Docker Compose baseline files.
- Add documentation and infrastructure folders for future phases.

### Scope

Included:

- Application package under `app/`.
- Manager route placeholder under `app/routes/manager.py`.
- Docker files.
- Test folder.
- Documentation folder.
- Terraform placeholder folder.

Excluded:

- Real authentication.
- Real CRUD endpoints.
- Real database migrations.
- Running containers.
- AWS deployment.

### Files Changed

- `README.md`
- `Roadmap.md`
- `.env.example`
- `.env.docker.example`
- `Dockerfile`
- `Dockerfile.multistage`
- `docker-compose.yml`
- `app/main.py`
- `app/config.py`
- `app/database.py`
- `app/logger.py`
- `app/routes/manager.py`
- `docs/*`
- `infra/*`
- `tests/*`

### How It Works

`app/main.py` creates the FastAPI app, exposes `/health`, exposes `/`, and registers the manager route group under `/api/manager`.

`app/config.py` reads environment variables for the app name, version, database URL, and JWT settings.

`app/database.py` prepares SQLAlchemy database access. It requires `DATABASE_URL`, so the application fails early if database configuration is missing.

### Security Notes

- Security headers were added in `app/main.py`.
- Secrets are not committed; examples live in `.env.example` and `.env.docker.example`.
- Real JWT handling is deferred to Phase 3.

### Verification

Completed:

- Python syntax compilation passed for scaffold Python files.
- Folder was renamed and re-scanned successfully as `apps/mecandjeo-mhc-monitoring`.

Deferred:

- Runtime import validation awaits a project environment or Docker image with dependencies installed.
- Docker execution will be verified in a later local validation phase.

### Known Gaps

- `ARCHITECTURE.md`, `PROJECT-STATUS.md`, `CHANGELOG.md`, and `CONTRIBUTING.md` are documentation files and will evolve as phases complete.
- Most route files are intentionally not created yet because each workflow phase will add only the routes it needs.

### Next Step

Phase 2 database design and model definition.