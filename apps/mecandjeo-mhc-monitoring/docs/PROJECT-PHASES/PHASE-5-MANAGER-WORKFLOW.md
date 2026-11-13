## Phase 5 - Manager Workflow

Status: Completed

### Purpose

Give managers a read-only operational view of MHC activity so they can supervise active work, identify live delays, and compare completed performance with context.

### Objectives

- Replace the manager placeholders with real dashboard endpoints.
- Let managers see active operators and their selected MHC numbers.
- Let managers see active shifts, tasks, and delays.
- Let managers review delay totals by delay type.
- Let managers compare performance by operator, crane, nature of work, or date.
- Keep manager routes protected by RBAC.

### Scope

Included:

- Dashboard summary endpoint.
- Live operator status endpoint.
- Active shift overview endpoint.
- Delay breakdown endpoint.
- Performance trends endpoint.
- Manager/admin-only access control.
- Phase 5 tests.

Excluded:

- Manager edits to operator records.
- CSV or PDF report export.
- Admin reference data management.
- PostgreSQL/Docker runtime validation.
- AWS deployment.

### Files Changed

- `app/routes/manager.py`
- `app/schemas.py`
- `app/services/dashboard_service.py`
- `app/services/delay_analysis_service.py`
- `app/services/performance_service.py`
- `tests/test_manager_workflow.py`
- `README.md`
- `ARCHITECTURE.md`
- `Roadmap.md`
- `PROJECT-STATUS.md`
- `CHANGELOG.md`
- `docs/3. API-DESIGN.md`
- `docs/5. SECURITY-RBAC.md`
- `docs/6. REPORTING-DASHBOARD.md`
- `docs/2. Project-Phases.md`

### How It Works

A manager logs in and receives a JWT. The manager uses that bearer token to call `/api/manager/*` endpoints. The route dependency checks that the current user is either a `manager` or an `admin`.

The dashboard service counts active shifts, active tasks, active delays, completed tasks, containers moved, and total delay minutes.

The live status service reads active shifts and shows whether each operator is active, working on a task, or delayed.

The delay analysis service groups delays by `delay_type` and `custom_delay_type`.

The performance service calculates task minutes, delay minutes, effective work minutes, container totals, and moves per hour from completed task logs.

### Security Notes

- All manager routes require a valid JWT.
- Manager routes require the `manager` or `admin` role.
- Operator users receive `403 Forbidden` on manager dashboard routes.
- Phase 5 manager endpoints are read-only.
- Report export remains protected but deferred to Phase 7.

### Verification

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -vv

PowerShell: `.\.venv\Scripts\python.exe -m pytest tests\test_manager_workflow.py -vv`
```

Git Bash: `./.venv/Scripts/python.exe -m pytest tests/test_manager_workflow.py -vv`



Result:

-  19 total tests passed. Tests cover dashboard values, trends, delay aggregation, RBAC, and invalid trend grouping.

Remaining warning:

- FastAPI/Starlette emits a deprecation warning about `TestClient` and future `httpx` usage. This does not fail the suite.

### Known Gaps

- Tests use SQLite for speed.
- PostgreSQL validation is deferred to the local Docker phase.
- Manager report exports are deferred to Phase 7.
- Admin reference data management is deferred to Phase 6.

### Next Step

Phase 6 admin workflow.

## Phase 6 - Admin Workflow