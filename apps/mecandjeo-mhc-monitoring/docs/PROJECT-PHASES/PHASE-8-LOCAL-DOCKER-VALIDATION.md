## Phase 8 - Local Docker Validation

Status: Completed

### Purpose

Verify that the FastAPI service can start with PostgreSQL through Docker Compose,
not only against the SQLite database used by automated API tests.

### Work Completed

- Added an explicit `AUTO_CREATE_SCHEMA` switch that is false by default and true only in `.env.docker`.
- Added startup connectivity and local schema initialization when that switch is enabled.
- Validated Python compilation, the complete 29-test suite, and the resolved Docker Compose configuration.
- Added PowerShell and Git Bash Docker verification commands.

## Important Files

- `app/config.py`, `app/database.py`, `app/main.py`
- `.env.example`, `.env.docker.example`, `docker-compose.yml`, `Dockerfile`
- `docs/1. LOCAL-DEVELOPMENT.md`

## Local Verification

PowerShell:

```powershell
docker compose --env-file .env.docker up --build -d
docker compose --env-file .env.docker ps
Invoke-RestMethod http://localhost:8004/health
docker compose --env-file .env.docker exec crane-db psql -U crane_user -d crane_monitoring -c "\dt"
docker compose --env-file .env.docker down
```

Git Bash:

```bash
docker compose --env-file .env.docker up --build -d
docker compose --env-file .env.docker ps
curl http://localhost:8004/health
docker compose --env-file .env.docker exec crane-db psql -U crane_user -d crane_monitoring -c '\dt'
docker compose --env-file .env.docker down
```

Result: both containers became healthy, `/health` returned `{"status":"ok"}`, and PostgreSQL contained all 13 application tables. The named database volume was retained after stopping containers.

### Security Notes

- `AUTO_CREATE_SCHEMA` is false by default and enabled only by `.env.docker` for local validation.
- Production must use versioned database migrations rather than automatic table creation.
- Docker environment files are ignored by Git and must use deployment-specific secrets outside local development.

### Known Gaps

- Database migrations remain pending.
- Automated tests use SQLite for fast isolated cases; Phase 8 verifies the same model metadata against PostgreSQL.
The full automated suite remains green: `.\.venv\Scripts\python.exe -m pytest tests -vv` gives 29 passed with potential to increase as more features are added.