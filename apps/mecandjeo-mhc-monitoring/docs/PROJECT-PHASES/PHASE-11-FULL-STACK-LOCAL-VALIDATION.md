## Phase 11 - Full-stack local validation

Status: Completed

### Purpose

Make `docker compose up` run the whole system (database, migrations, API and web app), and prove locally that it is healthy, secure and reproducible, so the cloud phases start from a stack that is already known to work.

### Objectives

- Serve the React app from a container (nginx) that also forwards `/api` to the API.
- Replace automatic table creation with versioned database migrations (Alembic), run by a one-off job.
- Add a browser end-to-end test of the whole system.
- Harden the containers: non-root users, no test tools in the image, health checks that report quickly, operating-system fixes at build time.
- Scan the Dockerfiles and images for known flaws and fix what is found.
- Lock the package versions so builds are repeatable.
- Add a one-command stack check, and document everything for a beginner.

### Deliverables

### 11A. Frontend container

1. **`frontend/Dockerfile`**
   - **Change:** New file. Uses two stages: Node builds the site, and `nginx-unprivileged` serves it. Applies operating-system fixes and ends with `USER 101`.

2. **`frontend/nginx.conf`**
   - **Change:** New file. Configures:
     - Port `8080`.
     - `/healthz` health endpoint.
     - Proxying of `/api/` and `/health` to `crane-app:8004`.
     - One-year cache for `/assets/`.
     - Fallback to `index.html`.
     - Security headers and compression.

3. **`frontend/.dockerignore`**
   - **Change:** New file.

4. **`docker-compose.yml`**
   - **Change:** Adds the `crane-web` service on `WEB_PORT` (default `8080`), starting after `crane-app` is healthy.

### 11B. Migrations

1. **`alembic.ini`, `migrations/env.py`, `migrations/script.py.mako`**
   - **Change:** New files. Provide Alembic settings, the migration runner, and the template for new migration files.

2. **`migrations/versions/0001_baseline.py`**
   - **Change:** New file. Creates the 13 tables, proven identical to what the models describe.

3. **`app/config.py`**
   - **Change:** Added the `RUN_BOOTSTRAP` setting.

4. **`app/main.py`**
   - **Change:** Start-up creates tables only if `AUTO_CREATE_SCHEMA` is on, and runs the bootstrap only if `RUN_BOOTSTRAP` is on.

5. **`docker-compose.yml`**
   - **Change:** Adds a new one-off service, `crane-migrate`, which runs `alembic upgrade head`. `crane-app` waits for it to complete successfully.

6. **`.env.docker.example`**
   - **Change:** Sets `AUTO_CREATE_SCHEMA=false` and `RUN_BOOTSTRAP=true`.

7. **`tests/test_migrations.py`**
   - **Change:** New test file containing 6 tests.

8. **`tests/test_lifespan.py`**
   - **Change:** New test file containing 4 tests.

### 11C. Browser tests (`e2e/`)

1. **`package.json`, `tsconfig.json`, `.gitignore`**
   - **Purpose:** Project setup for Playwright and TypeScript.

2. **`playwright.config.ts`, `global-setup.ts`**
   - **Purpose:** Define test settings and perform an early stop with a clear message when the application stack is down.

3. **`helpers/env.ts`, `helpers/ui.ts`**
   - **Purpose:** Provide admin login lookup and reusable UI actions for signing in, signing out, and adding a one-second pause.

4. **`tests/login.spec.ts`**
   - **Purpose:** Contains 4 browser tests.

5. **`tests/journey.spec.ts`**
   - **Purpose:** Contains 1 test covering the admin, operator, and manager journey, with its own cleanup.

6. **`cleanup-test-data.sql`**
   - **Purpose:** Removes data left behind by a failed test run. Only rows named `E2E-` or `e2e-` are removed.

### 11D. Hardening, verification and reproducibility

1. **`Dockerfile`**
   - **Change:** Uses a non-root user `app`, applies operating-system fixes (`apt-get upgrade`), installs packages from `requirements.lock`, and ensures files are owned by `app`.

2. **`requirements.txt`**
   - **Change:** Contains runtime packages only.

3. **`requirements-dev.txt`**
   - **Change:** New file. Includes `-r requirements.lock`, `httpx`, and `pytest`.

4. **`requirements.lock`**
   - **Change:** New file. Contains exact versions of the 25 packages (generated, not edited manually).

5. **`docker-compose.yml`**
   - **Change:** Health checks gain `start_interval: 2s` so containers report healthy in seconds.

6. **`scripts/verify_stack.sh`**
   - **Change:** New script. Runs 14 checks, displays `PASS` and `FAIL` lines, and returns an exit code.

7. **`scripts/scan_security.sh`**
   - **Change:** New script. Runs Trivy scans against the Dockerfiles and both images, with `--strict` for pipelines.

8. **`scripts/update_lock.sh`**
   - **Change:** New script. Safely regenerates `requirements.lock`.

9. **`.trivyignore`**
   - **Change:** New file. Documents accepted findings and the reasons for accepting them.

10. **`frontend/Dockerfile`**
    - **Change:** Uses `USER 101`, applies `apk upgrade`, and moves the base image to the maintained `stable-alpine` tag.                                       |

**Documentation**

1. **`docs/PROJECT-PHASES/Phase-10.2-Database-Migrations-Explained.md`**
   - **Purpose:** Explains database migrations, including concepts, files, commands, and how to add a new migration.

2. **`docs/PROJECT-PHASES/Phase-11.6-TESTING-GUIDE.md`**
   - **Purpose:** Compares every level of testing, with commands and expected results.

3. **`docs/PROJECT-PHASES/Phase-11.4-PLAYWRIGHT-GUIDE.md`**
   - **Purpose:** Provides a standalone guide to browser tests, including questions and answers.

4. **`docs/PROJECT-PHASES/Phase-11.1-CONTAINER-SECURITY.md`**
   - **Purpose:** Covers non-root containers, health checks, operating-system fixes, Trivy, reading reports, and responding to findings.

5. **`docs/PROJECT-PHASES/Phase-11.2-DEPENDENCY-LOCKING.md`**
   - **Purpose:** Explains lock files, the dependency update routine, rollback, base image policy, and Git practices for this application.

6. **`docs/PROJECT-PHASES/Phase-11.5-SCRIPTS-REFERENCE.md`**
   - **Purpose:** Documents every script, including its purpose, run-from folder, command, expected output, and exit codes.

7. **`docs/PROJECT-PHASES/Phase-11.3-DEVOPS-CONCEPTS-MAP.md`**
   - **Purpose:** Maps the DevOps concepts used in the application to their relevant files, commands, and later phases.

8. **`docs/1. LOCAL-DEVELOPMENT.md` and `docs/PROJECT-PHASES/Phase-10.1-Frontend-Development.md`**
   - **Purpose:** Updated to cover the four-container stack, database migrations, 71 tests, and port `8080`.

### How It Works

1. `docker compose --env-file .env.docker up -d --build --wait` starts four containers: `crane-db` (PostgreSQL), `crane-migrate` (runs `alembic upgrade head` and exits with code 0), `crane-app` (the API, started after the migration succeeded) and `crane-web` (nginx).
2. The browser talks only to `http://localhost:8080`. nginx serves the built site and forwards `/api/` and `/health` to the API, so no CORS settings are needed. Unknown paths return `index.html` so a page refresh keeps the user on the right screen.
3. Tables come from migrations only. The API no longer creates tables (`AUTO_CREATE_SCHEMA=false`); the idempotent bootstrap still adds reference data, sample cranes and the first admin (`RUN_BOOTSTRAP=true`).
4. Both application containers run as ordinary users (`app`, uid 999; `nginx`, uid 101). The backend image holds only runtime packages, installed from `requirements.lock`.
5. Operating-system fixes are applied at every build (`apt-get upgrade`, `apk upgrade`); Python and npm packages stay locked.
6. Health checks run every two seconds while a container starts (`start_interval`), so `up --wait` returns within seconds of readiness.
7. `scripts/verify_stack.sh` asks the stack 14 questions, including whether the image contains exactly the versions in `requirements.lock`. `scripts/scan_security.sh` runs Trivy as a container and ends with distinct exit codes so a pipeline can use it.
8. The browser test creates its own crane, operator and manager with unique names, runs a shift end to end, checks the manager's view and the CSV download, and retires what it created.

### Security Notes

- Containers run as non-root, and files in the backend image are owned by the unprivileged user. The Dockerfile scan (`DS-0002`) now passes for both images; an unused experimental Dockerfile with the same finding was deleted.
- The production image contains no test tools.
- Image scans found real, fixable flaws during the phase and each was fixed at the right layer: an old base tag (61 findings in the web image), operating-system packages (`curl`, `libexpat`, `brotli-libs` on Alpine; `apt` and `zlib1g` on Debian). Both images and the Dockerfiles ended clean.
- The only accepted finding is `DS-0026` (no `HEALTHCHECK` inside the Dockerfile), recorded with its reason in `.trivyignore`; health checks are defined where the containers run.
- `.env.docker` stays out of Git. The browser test reads the admin password from it and never stores it.
- The browser test creates real data, so it must only be pointed at the local stack.
- A database backup (`~/backup_before_phase11.sql`) contains password hashes and must be deleted now that the phase is verified.

### Tests

- **Backend:** 71 passed in 12 files (61 earlier, plus 6 migration and 4 start-up tests).
- **Frontend:** 107 passed in 16 files; lint and build clean.
- **Browser:** 6 passed (4 sign-in tests, the journey, and one added by the owner).
- **Stack check:** `verify_stack.sh` reports 14 passed, 0 failed.
- **Security scan:** `scan_security.sh --strict` reports `[CLEAN]` for the Dockerfiles and both images, exit code 0.
- The backend suite passes on the locked package versions installed on the developer's Windows machine.

### Acceptance Checks (all verified)

- A fresh rebuild (`down -v`, `up -d --build`, then the seed script) gave a working system with all browser checks passing.
- `crane-migrate` ends `Exited (0)`; `crane-db`, `crane-app` and `crane-web` are `(healthy)`.
- `curl http://localhost:8080/healthz` returns 200; `/health` through nginx returns `{"status":"ok"}`; `/operator` returns 200; assets carry `max-age=31536000`.
- `exec crane-app id` shows uid 999 and `exec crane-web id` shows uid 101.
- `alembic current` reports `0001 (head)` and `alembic check` reports no differences.
- Stopping `crane-web` made 6 of the checks fail with clear hints, and starting it made all pass again; a deliberately older image was detected by the lock check.
- The image's installed packages equal `requirements.lock`.
- `python -m pytest tests -q` ends with `71 passed`; `cd e2e && npm test` ends with `6 passed`.

### Known Gaps

- The token still lives in `sessionStorage` with no refresh token, and a password change does not cancel tokens already issued (they expire after 24 hours).
- Themes are saved in the browser, not the database.
- Managers cannot filter reports by operator, because the user list is admin-only.
- nginx sends security headers but no Content-Security-Policy.
- Lock files record versions but not checksums (`--require-hashes` is a later hardening).
- Base images follow maintained tags instead of pinned digests; automatic update proposals (Dependabot or Renovate) belong to the pipeline phase.
- Operating-system packages are updated at build time, so two builds can differ slightly; the scan is the safety net.
- The web image still contains optional nginx modules that this project does not use (for example the XSLT module that pulls in libxslt). The -slim variant of the base image leaves them out and should be evaluated as a follow-up hardening step.
- Backend tests use SQLite. PostgreSQL is exercised by the browser tests and the stack check.
- A failed browser run leaves test data behind; `e2e/cleanup-test-data.sql` removes it.
- Secret scanning of the code folder is not part of the scan script yet.
- The application folder is under version control locally; nothing is pushed to the remote without explicit approval.

### Next Step

Phase 12: AWS infrastructure with Terraform (network, container service, load balancer, database and logging). The migration job and the bootstrap will run as one-off tasks against an empty cloud database, and the same scripts and checks will gate the deployment.

---

## Roadmap Update

| Phase | Name                               | Status    |
|-------|------------------------------------|-----------|
|   9   | Local readiness (backend)          | Completed |
|  10   | Frontend UI (React and TypeScript) | Completed |
|  11   | Full-stack local validation        | Completed |
|  12   | AWS infrastructure                 | Next      |
|  13   | End-to-end deployment              | Planned   |
|  14   | Frontend CI/CD with GitHub Actions | Planned   |
|  15   | Kubernetes foundations             | Planned   |
|  16   | Helm packaging                     | Planned   | 
|  17   | Argo CD GitOps                     | Planned   |
|  18   | Observability and reliability      | Planned   |
|  19   | Demonstration readiness            | Planned   |

Replace **Immediate Next Step** with:

```markdown
## Immediate Next Step

Begin Phase 12 (AWS infrastructure): describe the network, container
service, load balancer, database and logging with Terraform. The images,
migration job, verification script and security scan built in Phase 11
carry over unchanged.
```

## Corrections to Earlier Entries

Update the numbers and statements that this phase superseded:

- **Phase 9 and Phase 10 entries:** the backend suite is now 71 tests in 12 files.
- **Phase 10 "Known Gaps":** "There is no production container yet", "database tables are still created automatically (no migrations), and the Dockerfile runs as root" and "There are no end-to-end browser tests yet" are all resolved in Phase 11. Mark them as resolved, or remove them.
- **Phase 10 "Next Step":** replace with "Completed in Phase 11".

## Housekeeping Before Closing the Phase

- [ ] Delete `~/backup_before_phase11.sql` (it holds password hashes).
- [ ] Delete `requirements.lock.EXAMPLE` if you saved it into the project (nothing uses it).
- [ ] Confirm `.env.example` and `.env.docker.example` hold only placeholder values.
- [ ] Create the first local commit of the app (`docs/PROJECT-PHASES/Phase-11.2-DEPENDENCY-LOCKING.md`, section 12.3). Do not push without approval.
