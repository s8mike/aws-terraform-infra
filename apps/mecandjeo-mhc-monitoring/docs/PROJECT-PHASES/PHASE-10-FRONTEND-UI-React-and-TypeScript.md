## Phase 10 - Frontend UI

Status: Completed

### Purpose

Give operators, managers and admins a working web interface on top of the local API, so the whole system can be used and demonstrated locally before any cloud work.

### Objectives

- Build a React and TypeScript application with login, role-based screens and session handling.
- Operator screen: start and end shifts, tasks and delays, and record working conditions.
- Manager screen: live overview, delay breakdown, performance trends and reports with CSV download.
- Admin screen: manage users, cranes and reference data.
- Let every user change their own password, and choose a color theme.
- Add the backend support the screens need, with tests.
- Add automated frontend tests and complete beginner documentation.

### Deliverables [Files vs Changes]

#### Backend

1. **`app/routes/operators.py`**
   - Added `GET /api/operators/me/active` and `GET /api/operators/me/shifts/{id}/summary`.

2. **`app/services/operator_service.py`**
   - Added `build_operator_active_state` and `build_shift_summary`.

3. **`app/schemas.py`**
   - Added `OperatorActiveStateRead`, `ShiftSummaryRead`, and `PasswordChange`.

4. **`app/routes/auth.py`**
   - Added `POST /api/auth/change-password` (204, audited).

5. **`app/db/seed_data.py`**
   - Restructured work types and working areas, with explicit labels (28 reference values).

6. **`scripts/seed_demo_data.sh`**
   - New script. Creates demo accounts and sample work through the API.

7. **`tests/test_change_password.py`**
   - New test file containing 9 tests.

8. **`tests/test_operator_workflow.py`**
   - Added 4 tests covering active state and per-shift totals.

9. **`tests/test_reference_validation.py` and `tests/test_lookups.py`**
   - Updated for the new work types and working areas.

**Frontend (`frontend/`)**

| Area                    | Contents                                                                   |
|-------------------------|----------------------------------------------------------------------------|
| Tooling                 | Vite, React 19, TypeScript, React Router, Vitest, Testing Library, oxlint  |
| `src/api/`              | One typed API client plus calls for auth, operator, manager and admin      |
| `src/auth/`             | Sign-in state, session restore, role guards                                |
| `src/pages/`            | Login, operator, manager and admin screens                                 |
| `src/components/`       | Panels, forms, tabs, tables, cards, password field, change-password dialog |
| `src/theme/`            | Soft, Light, Grey and Dark themes, saved per user                          |
| `src/**/*.test.ts(x)`   | 107 tests in 16 files                                                      |
| `scripts/test-here.mjs` | Runs the tests of the folder you are standing in                           |

**Documentation** [Files vs Purpose]

1. **`docs/PROJECT-PHASES/Phase-10.1-Frontend-Development.md`**
   - **Purpose:** Step-by-step guide covering installation, running the frontend, scripts, test commands, and explanations of all 107 tests.

2. **`docs/7. Frontend-Structure.md`**
   - **Purpose:** Provides a one-line explanation of each frontend folder and file.

3. **`docs/1. LOCAL-DEVELOPMENT.md`**
   - **Purpose:** Backend development runbook, updated test counts, demo data script, and explanations of all 61 backend tests.                                                                                              |

### How It Works

1. In development the browser talks only to `http://localhost:5173`. Vite forwards `/api` and `/health` to the backend on port 8004, so no CORS settings are needed.
2. After login the token is kept in `sessionStorage` and sent as a Bearer header. Any `401` on an authenticated call clears it and returns the user to the login page.
3. The operator screen reloads its state from `GET /api/operators/me/active`, so a page refresh never loses the open shift, task or delay.
4. "This shift" figures come from the per-shift summary and start at zero for every new shift; "All time" figures stay separate.
5. Times are sent and stored as naive UTC and shown in the viewer's local time.
6. Operators choose work types and areas from `GET /api/lookups`, which lists only active values. The API rejects anything else.
7. The manager overview refreshes itself every 15 seconds. Reports and the CSV download share the same filters.
8. The theme is applied to the page and remembered per user in that browser.

### Standard values after this phase

1. **Nature of work (5)**
   - Discharging (includes imports)
   - Loading
   - Loading - Empties
   - Loading - OOG
   - Other

2. **Working area (8)**
   - Port Side
   - Starboard Side
   - Deck Free Bay
   - Across Heights Portside
   - Underdeck Free Bay
   - Underdeck Across Heights
   - Tight Space
   - Other

3. **Delay type (12)**
   - Unchanged.

4. **Shift code (3)**
   - A, B, C (fixed in the backend).

### Security Notes

- A wrong current password on change-password returns `400`, not `401`, so a typo does not sign the user out.
- New passwords follow the same policy as registration and admin resets (8 or more characters with a lowercase letter, an uppercase letter, a number and one of `! @ # % $`), checked in the browser first and again by the API.
- The change is written to the audit log as `user.password_changed`; no password is ever logged.
- Admins cannot deactivate or demote themselves; the UI also hides those controls.
- Role guards in the frontend are a convenience only. The backend remains the real authority and returns `403` for the wrong role.
- Locked reference-data codes cannot be edited because past records store them.
- `.env.docker` stays out of Git. The demo accounts share one documented password and are for local use only.

### Tests

- **Backend:** 61 passed (47 from Phase 9, plus 9 change-password, 4 operator, 1 reference-validation).
- **Frontend:** 107 passed in 16 files (`npm run test`), also runnable per folder.
- `npm run build` (type-checks the tests too) and `npm run lint` finish clean (0 warnings, 0 errors).
- The date-sensitive frontend tests pass in several time zones.
- Explanations of every test: `docs/1. LOCAL-DEVELOPMENT.md` section 11 and `docs/PROJECT-PHASES/Phase-10.1-Frontend-Development.md` section 9.

### Acceptance Checks (all verified)

- `python -m pytest tests -q` ends with `61 passed`.
- `npm run test` reports 16 files and 107 tests passed; `npm run build` and `npm run lint` are clean.
- Login works for operator, manager and admin, each landing on its own screen; other screens redirect.
- Operator: shifts, tasks, delays and conditions work in order; the red notices block ending a task during a delay and a shift during a task; a new shift starts at zero.
- Manager: overview, delays, performance (by operator, crane, nature of work and date) and reports match the demo data, and the CSV downloads.
- Admin: users, cranes and reference data can be added, edited and retired; changes appear in the database and the audit log.
- Change password works from the header and the old password stops working.
- All four themes display correctly and survive a refresh, separately for each user.

### Known Gaps

- The frontend runs through the Vite dev server only. There is no production container yet.
- The token lives in `sessionStorage` with no refresh token. A password change does not cancel tokens already issued; they expire after 24 hours.
- Themes are saved in the browser, not the database, so they do not follow a user to another computer.
- Past working-condition records cannot be listed; the form only confirms each save.
- Managers cannot filter reports by operator, because the user list is admin-only.
- "By date" grouping uses the UTC date of each task.
- There is no self-registration screen. Operators are created by an admin or through the API.
- Confirmations use the browser's own dialog.
- There are no end-to-end browser tests yet; the unit and component tests use a simulated browser.
- The test suite takes about 30 seconds because each file starts its own simulated browser.
- Users, cranes and reference values are retired, never deleted.
- Carried over: database tables are still created automatically (no migrations), and the Dockerfile runs as root.

### Next Step

Phase 11: full-stack local validation. Add a frontend container (Node build served by nginx with an `/api` proxy), a `docker compose` service for it, database migrations, and a browser end-to-end smoke test, so `docker compose up` runs the whole system.

---

## Roadmap Update

| Phase   | Name                               | Status    |
|---------|------------------------------------|-----------|
|   9     | Local readiness (backend)          | Completed |
|   10    | Frontend UI (React and TypeScript) | Completed |
|   11    | Full-stack local validation        | Next    |
|   12    | AWS infrastructure                 | Planned |
|   13    | End-to-end deployment              | Planned |
|   14    | Frontend CI/CD with GitHub Actions | Planned |
|   15    | Kubernetes foundations             | Planned |
|   16    | Helm packaging                     | Planned |
|   17    | Argo CD GitOps                     | Planned |
|   18    | Observability and reliability      | Planned |
|   19    | Demonstration readiness            | Planned |
