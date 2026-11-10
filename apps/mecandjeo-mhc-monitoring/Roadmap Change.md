Your roadmap answers my frontend-stack question: React and TypeScript, planned as Phase 11. The review below is based on that.

## What's wrong with the current roadmap

1. **The frontend comes after cloud deployment.** It sits at Phase 11, after Phases 9-10, which contradicts your goal of a working local app first.
2. **Phase 10's acceptance check can't pass.** "Operator, manager, and admin flows work end to end" can't be verified without a UI.
3. **Database migrations appear nowhere.** Phase 9 puts the app on RDS, and `AUTO_CREATE_SCHEMA` must stay off outside local use. Alembic has to exist before Phase 9.
4. **Local readiness blockers aren't scheduled.** These are the first-admin bootstrap, seeded cranes, and operator-readable lookups (operators can't call the admin-only `/api/cranes` or `/api/admin/reference-data`). A fresh database can't start a shift today.
5. **One correction to my earlier message:** I suggested CORS. Skip it. Use the Vite dev proxy locally, an nginx proxy in Docker and ALB path routing in AWS, so the browser only ever talks to one origin.
6. **Frontend work is split awkwardly.** The UI is in Phase 11 and containerization is in Phase 12. Both belong before AWS.
7. **"Immediate Next Step" points at Phase 9 (AWS).** It must change.

## Revised phase order

| Phase | Name                                                     | Source                   |
|-------|----------------------------------------------------------|--------------------------|
| 9     | Local readiness (backend)                                | New                      |
| 10    | Frontend UI                                              | Old 11                   |
| 11    | Full-stack local validation                              | New, plus part of old 12 |
| 12    | AWS infrastructure                                       | Old 9                    |
| 13    | End-to-end deployment                                    | Old 10                   |
| 14    | Frontend CI/CD (GitHub Actions)                          | Old 12, remainder        |
| 15-19 | Kubernetes, Helm, Argo CD, observability, demo readiness | Old 13-17                |

You move from ECS in Phases 12-13 to Kubernetes in Phase 15. That is fine as a learning path, but only the container images and health endpoints carry over. Keep both containers 12-factor (config only from env vars) so they do.

## Phase 9 - Local readiness (backend)

- `app/db/bootstrap.py`: creates the first admin from `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD`, idempotent, run with `python -m app.db.bootstrap`. It lives inside `app/` so the Docker image includes it.
- `app/db/seed_data.py`: add sample cranes, gated by `SEED_SAMPLE_DATA` (default `false`, `true` only in `.env.docker`).
- `app/config.py` and the `.env*.example` files: add the three new variables.
- `app/routes/lookups.py` and `app/schemas.py`: `GET /api/lookups` for any authenticated role. It returns active work types, working areas, delay types, shift labels and active `{id, mhc_number}` cranes.
- `app/main.py`: register the router.
- `app/services/operator_service.py`: validate `nature_of_work`, `working_area` and `delay_type` against active `reference_data`. `custom_delay_type` stays free text. This closes the Phase 6 gap, and reports group by these values. It is the riskiest item for the existing 29 tests, so `tests/conftest.py` must seed reference data.
- `tests/test_lookups.py` and `tests/test_bootstrap.py`: lookups return 200 for operator, manager and admin and 401 without a token, inactive records are excluded, and a second bootstrap run changes nothing.
- **Exit:** the full suite passes, and on a fresh Docker volume the bootstrap leaves you able to log in as admin with cranes available.

## Phase 10 - Frontend UI

- Location: `apps/mecandjeo-mhc-monitoring/frontend/` (React, TypeScript, Vite), self-contained like the rest of the app.
- API calls go to relative `/api/...` paths. `vite.config.ts` proxies `/api` and `/health` to `http://localhost:8000`.
- Build order:
  1. Login, token handling (in memory plus `sessionStorage`), and a 401 redirect to login. There are no refresh tokens, so expiry forces re-login.
  2. Role-based routing.
  3. Operator screens: shift start (MHC and A/B/C), task, delay, working conditions, shift end. The UI must enforce the Phase 4 rules: no closing a task during an active delay, and no closing a shift during an active task.
  4. Manager screens: dashboard, live status, delay breakdown, performance filters, CSV download.
  5. Admin screens: users, cranes, reference data.
- **Exit:** all three roles work against the API running locally, and Vitest covers login and the operator state rules.

## Phase 11 - Full-stack local validation

- `frontend/Dockerfile` (node build, then nginx) and `frontend/nginx.conf` (proxy `/api` and `/health` to `crane-app`).
- `docker-compose.yml`: add a `crane-web` service.
- Alembic: `alembic.ini`, `migrations/`, and a baseline revision from the current models. Compose runs `alembic upgrade head`, and `AUTO_CREATE_SCHEMA` is used only by the SQLite tests.
- `frontend/e2e/smoke.spec.ts` (Playwright): admin creates an operator, the operator runs a full shift with a delay, the manager sees it live, the manager downloads a CSV, and the CSV row matches.
- **Exit:** `docker compose down -v && docker compose up --build` on a clean volume brings up db, api and web, and the smoke test passes on PostgreSQL.

## Phases 12-13 (changes only)

- Phase 12 adds a web ECS service and target group. ALB rules route `/api/*` and `/health` to the API and everything else to web.
- Migrations run as a one-off ECS task before each service update.
- `SECRET_KEY`, database credentials and the bootstrap admin password come from Secrets Manager or SSM, never from `.env` files.
- Phase 13's acceptance check stays as written, now verifiable through the UI.

## Edits to `Roadmap.md`

Replace "Immediate Next Step" with:

```markdown
## Immediate Next Step

Begin Phase 9 (local readiness): first-admin bootstrap, sample crane seed data, the `/api/lookups` endpoint, and reference-data validation on operator endpoints. AWS work starts only after Phase 11 passes locally.
```

Also:
- Replace "Execution Order" items 9-10 with the new table.
- Renumber the post-Phase-10 list from 11-17 to 14-19 as shown above.
- Add `frontend/`, `app/db/bootstrap.py`, `app/routes/lookups.py` and `migrations/` to the application structure tree.
- Update the Phase 10 and Phase 13 acceptance checks to say the flows are verified through the UI.

## Files I need to start Phase 9

Please upload these:
- `app/main.py`
- `app/config.py`
- `app/db/seed_data.py`
- `app/services/operator_service.py`
- `app/routes/cranes.py`
- `app/routes/admins.py`
- `tests/conftest.py`
- `docker-compose.yml`
- `.env.docker.example`
- `Dockerfile`

For Phase 10, I'll also need `app/schemas.py` and the route files (`shifts.py`, `task_logs.py`, `delay_logs.py`, `working_conditions.py`, `operators.py`, `manager.py`, `reports.py`, `auth.py`), so the TypeScript API client matches the real payloads.