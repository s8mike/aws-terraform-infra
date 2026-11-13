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

### Deliverables [Files and Changes]

1. **`app/config.py`**
   - Added `BOOTSTRAP_ADMIN_EMAIL`, `BOOTSTRAP_ADMIN_PASSWORD`, and `SEED_SAMPLE_DATA`.

2. **`app/db/bootstrap.py`**
   - New file. Implements an idempotent first-run bootstrap for reference data, optional sample cranes, and the first admin.

3. **`app/db/seed_data.py`**
   - Added `seed_sample_cranes` and `SAMPLE_CRANE_NUMBERS` (`MHC-01` to `MHC-03`).

4. **`app/routes/lookups.py`**
   - New file. Provides `GET /api/lookups`, available to operator, manager, and admin.

5. **`app/schemas.py`**
   - Added `LookupValueRead`, `LookupCraneRead`, and `LookupsRead`.

6. **`app/main.py`**
   - Registered the lookups router, ran bootstrap after schema creation, and corrected the `Permissions-Policy` header name.

7. **`app/auth.py`**
   - Replaced `OAuth2PasswordBearer` with `HTTPBearer` so Swagger accepts a pasted token.

8. **`app/services/operator_service.py`**
   - Added `validate_reference_value`.

9. **`app/routes/task_logs.py`**
   - Task start now validates `nature_of_work` and `working_area`.

10. **`app/routes/delay_logs.py`**
    - Delay start now validates `delay_type`.

11. **`tests/conftest.py`**
    - Added the opt-in `seeded_reference_data` fixture.

12. **`tests/test_bootstrap.py`**
    - New file containing 6 tests.

13. **`tests/test_lookups.py`**
    - New file containing 6 tests (3 from one parametrized test).

14. **`tests/test_reference_validation.py`**
    - New file containing 6 tests.

15. **`tests/test_operator_workflow.py`**
    - Applied the `seeded_reference_data` fixture to every test in the file.

16. **`tests/test_manager_workflow.py`**
    - Applied the `seeded_reference_data` fixture to every test in the file.

17. **`tests/test_reports.py`**
    - Applied the `seeded_reference_data` fixture to every test in the file.

18. **`.env.docker.example`**
    - Added bootstrap and sample-data settings, a longer `SECRET_KEY` placeholder, and `admin@example.com`.

19. **`docs/1. LOCAL-DEVELOPMENT.md`**
    - Rewritten as a beginner runbook.

### How It Works

1. When `AUTO_CREATE_SCHEMA=true` (local only), the API creates tables, then runs the bootstrap.
2. Bootstrap inserts any missing reference values (30 in total), inserts sample cranes only when `SEED_SAMPLE_DATA=true`, and creates the admin only when the email and password settings exist and no account with that email exists.
3. The bootstrap prints one line: `bootstrap: reference_data_added=N cranes_added=N admin_created=True|False`. Running it again prints zeros and `False`.
4. `GET /api/lookups` returns active reference values in four groups (`nature_of_work`, `working_area`, `delay_type`, `shift_code`) plus active cranes as `{id, mhc_number}`.
5. When an operator starts a task or delay, the submitted values are trimmed, lower-cased, and compared with active reference data. Unknown or retired values return `400`. `custom_delay_type` remains free text.

### Security Notes

- The bootstrap password is read from the environment, never from code, and is stored only as a bcrypt hash.
- A password shorter than 12 characters stops startup with an explicit error.
- Bootstrap never changes an existing account, so restarting cannot reset or take over an admin.
- Bootstrap creation is written to the audit log (`user.bootstrapped`).
- `/api/lookups` is read-only and requires a valid token. It exposes no user data and only active records.
- Sample cranes are controlled by `SEED_SAMPLE_DATA`, which must stay off outside local development.
- Missing tokens and invalid tokens both return `401` with the `WWW-Authenticate` header.
- `.env.docker` is ignored by Git. Real secrets must come from a secrets manager in cloud environments.

### Tests

```bash
python -m pytest tests -q
```

- Total: 47 passed (29 earlier tests plus 18 new).
- New coverage: bootstrap behaviour and idempotence, lookup access by role, hidden inactive values, reference validation, and value normalization.
- Test explanations are in `docs/1. LOCAL-DEVELOPMENT.md`, section 11.

### Acceptance Checks (all verified)

- `python -m pytest tests -q` ends with `47 passed` or more as new features are added.
- Both Docker containers report `healthy`.
- First start logs `reference_data_added=30` and, on a fresh volume, `admin_created=True`; the rebuild that introduced sample cranes logged `cranes_added=3`; later starts log zeros and `False`.
- The bootstrap admin can log in and obtain a token of about 176 characters.
- `GET /api/lookups` returns `401` without a token, and `200` with 10 work types, 5 working areas, 12 delay types, and 3 shift codes with one.
- An operator can see 3 active cranes through `/api/lookups` and start a shift on `MHC-01` (shift id 1 in the local test).
- On PostgreSQL, a task with an invalid work type returns `400` and a task with a valid work type returns `active`.

### Known Gaps

- No frontend exists yet. Operators, managers, and admins can use the API only through Swagger or scripts.
- Database tables are created with `AUTO_CREATE_SCHEMA`. Migrations are still needed before any cloud database.
- The Dockerfile runs as root and should use a non-root user before cloud deployment.
- Tokens last 24 hours with no refresh. The frontend must send the user back to login on `401`.
- Existing task and delay rows keep their stored strings. Only new writes are validated.
- Shift codes remain fixed to A, B, and C in code. They are not admin-editable.
- Routes registered at `/` (for example cranes) require the trailing slash: `/api/cranes/`.
- The bootstrap admin password has no rotation flow yet.

### Next Step

Phase 10: build the React and TypeScript frontend against the working local API (login, operator, manager, and admin screens).

## Roadmap Renumbering

Because local readiness, the frontend, and full-stack validation now come before any cloud work, replace the old Phase 9 to Phase 17 numbering with this table.

| Phase | Name                               | Source |
|-------|------------------------------------|--------|
| 9     | Local readiness (backend)          | New, completed |
| 10    | Frontend UI (React and TypeScript) | Old 11 |
| 11    | Full-stack local validation (frontend container, migrations, browser smoke test) | New, plus part of old 12 |
| 12    | AWS infrastructure                 | Old 9 |
| 13    | End-to-end deployment              | Old 10 |
| 14    | Frontend CI/CD with GitHub Actions | Old 12, remainder |
| 15    | Kubernetes foundations             | Old 13 |
| 16    | Helm packaging                     | Old 14 |
| 17    | Argo CD GitOps                     | Old 15 |
| 18    | Observability and reliability      | Old 16 |
| 19    | Demonstration readiness            | Old 17 |
