## Phase 7 - Reports And Exports

Status: Completed

### Purpose

Turn completed operator records into reusable historical evidence, so managers can assess performance with the delay context that affected the work.

### Objectives

- Return a filterable historical performance report.
- Export task-level results to CSV.
- Preserve export metadata for later review.
- Prepare the report structure that a future PDF renderer will use.

### Scope

Included:

- JSON report at `/api/reports/performance`.
- CSV download at `/api/reports/performance.csv`.
- Export-history endpoint at `/api/reports/exports`.
- Date, operator, crane, and nature-of-work filters.
- Completed-task totals for task time, delay time, effective work time, containers, and moves per hour.
- Task delay reasons and aggregate delay breakdown.
- `report_exports` metadata created for each CSV download.
- Phase 7 API tests.

Excluded:

- PDF file generation.
- Durable report file storage; CSV is streamed directly to the requester.
- PostgreSQL Docker validation and AWS/S3 deployment.

### Files Changed

- `app/routes/reports.py`
- `app/services/report_service.py`
- `app/schemas.py`
- `app/main.py`
- `app/routes/manager.py`
- `tests/test_reports.py`
- reporting, API, security, phase, status, and local-development documentation

### How It Works

A manager or admin requests completed tasks by date and optional operator, crane, or work-type filters. The service calculates each task's duration, adds its completed delays, derives effective work time, and calculates moves per hour. It returns a report summary, task rows, and a grouped delay breakdown.

The CSV route uses that same report object, so the screen response and download stay consistent. It streams the file in the HTTP response rather than relying on temporary container storage. A completed `report_exports` record stores who requested it, its type, format, dates, and the inline delivery marker.

### Security Notes

- JSON reports, CSV exports, and export history require a valid manager or admin JWT.
- Operator users receive `403 Forbidden`.
- Managers see only their own export metadata; admins can inspect all export metadata.
- CSV data is not stored in the application container, which avoids leaving potentially sensitive operational files behind.

### Verification

PowerShell:

```powershell
.\.venv\Scripts\python.exe -m compileall app tests
.\.venv\Scripts\python.exe -m pytest tests -vv
```

Git Bash:

```bash
./.venv/Scripts/python.exe -m compileall app tests
./.venv/Scripts/python.exe -m pytest tests -vv
```

Result:

- Python compilation passed.
- 29 tests passed with potential to increase as other features are being added.
- One non-blocking FastAPI/Starlette `TestClient` deprecation warning remains.

### Known Gaps

- PDF rendering and S3/object-storage delivery are deferred to a future deployment-focused enhancement.
- Tests use SQLite; PostgreSQL validation is planned for Phase 8.
- CSV export metadata records a delivery marker, not a permanent object URL.

### Next Step

Phase 8 local Docker validation.

## Remaining Phases

8. Local Docker validation.
9. Local readiness (backend)
10. Frontend UI (React and TypeScript)
11. Full-stack local validation
12. AWS infrastructure.
10. End-to-end deployment.
