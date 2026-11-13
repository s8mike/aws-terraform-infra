## Phase 4 - Operator Workflow

Status: Completed

### Purpose

Allow operators to log the work they actually perform during an MHC shift, including their selected MHC number, Shift A/B/C, task activity, delay activity, working conditions, and personal summary.

### Objectives

- Start and end an operator shift.
- Require operators to select Shift A, B, or C.
- Start and end task logs.
- Start and end delay logs.
- Capture working conditions.
- Require end timestamps when closing shifts, tasks, and delays.
- Prevent managers from using operator-only routes.
- Explain test purpose for future users.

### Scope

Included:

- Operator-only summary route.
- Shift lifecycle route.
- Task lifecycle route.
- Delay lifecycle route.
- Working-condition route.
- Operator workflow service helpers.
- Phase 4 tests.

Excluded:

- Manager dashboard aggregation.
- Admin-managed reference data.
- PostgreSQL/Docker runtime validation.
- Database migrations.

### Files Changed

- `app/main.py`
- `app/schemas.py`
- `app/db/seed_data.py`
- `app/services/operator_service.py`
- `app/routes/operators.py`
- `app/routes/shifts.py`
- `app/routes/task_logs.py`
- `app/routes/delay_logs.py`
- `app/routes/working_conditions.py`
- `tests/test_auth.py`
- `tests/test_operator_workflow.py`
- `docs/Questions-Updates.md`
- phase documentation files

### How It Works

An operator logs in, receives a JWT, and uses that token to start a shift. The shift start request includes the selected MHC number and shift code. The API looks up the active crane by MHC number, validates the shift code as A, B, or C, and creates an active shift owned by the current operator.

The operator can then start one task, log delays against that task, end delays, end the task, record working conditions, and finally end the shift. A task cannot close while a delay is still active. A shift cannot close while a task is still active.

### Security Notes

- Operator routes require a valid bearer token.
- Operator routes require the `operator` role.
- Operators can only work with their own records.
- Managers are rejected from operator routes.
- Registration now enforces stronger password complexity.

### Verification

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -vv

PowerShell: `.\.venv\Scripts\python.exe -m pytest tests\test_operator_workflow.py -vv`
```
Git Bash: `./.venv/Scripts/python.exe -m pytest tests/test_operator_workflow.py -vv`


Result:

- 15 total tests passed. Test comments explain complete lifecycle, invalid shift codes, RBAC, and active-delay protection.

Remaining warning:

- FastAPI/Starlette emits a deprecation warning about `TestClient` and future `httpx` usage. This does not fail the suite.

### Known Gaps

- Tests use SQLite for speed.
- PostgreSQL validation is deferred to the local Docker phase.
- Admin-managed reference data is deferred to the admin workflow phase.

### Next Step

Phase 5 manager workflow.