<!-- SCRIPTS-REFERENCE.md: one page listing every script and helper command of the project, with what it does, where to run it, the exact command and the output you should see. -->

# Scripts Reference

Every script and helper command used in this project, in one place. For each one you will find what it does, when to use it, the folder to run it from, the exact command, the output you should see, and what to do when it does not match.

Commands are for **Git Bash**. Unless a section says otherwise, run everything from:

```bash
cd /c/Users/Home/Documents/MY-DEVOPS-WORKS/PROJECTS/vpc-aws-terraform-infra/apps/mecandjeo-mhc-monitoring
```

## Contents

1. How to read this page
2. Inventory
3. `scripts/verify_stack.sh` (is the whole stack healthy?)
4. `scripts/scan_security.sh` (security scan)
5. `scripts/update_lock.sh` (refresh the locked Python packages)
6. `scripts/seed_demo_data.sh` (demo accounts and sample work)
7. `e2e/cleanup-test-data.sql` (remove leftovers of a failed browser test)
8. The `e2e` npm scripts (browser tests)
9. Docker Compose and Alembic one-liners
10. Exit code cheat sheet
11. How these become pipeline steps

---

## 1. How to read this page

**Exit codes.** Every program ends with a number. `0` means success and anything else means failure. You rarely see it, but pipelines (such as the GitHub Actions in Phase 14) read it to decide whether to continue or stop. To see the code of the last command in Git Bash:

```bash
echo "exit code: $?"
```

**Run-from folder.** Scripts use relative paths (`.env.docker`, `requirements.txt`, `e2e/`), so they must be run from `apps/mecandjeo-mhc-monitoring`. Each script says so when you run it from the wrong place.

**Reading a script.** All scripts start with comment lines that say what they do, and a `--help` option where it makes sense. Open any of them in an editor; they are written to be read.

## 2. Inventory

1. **`scripts/verify_stack.sh`**
   - **What it does:** Performs 14 checks covering containers, web, API, database, security, locked packages and login.
   - **Run from:** App folder.
   - **Command:**
     ```bash
     bash scripts/verify_stack.sh
     ```

2. **`scripts/scan_security.sh`**
   - **What it does:** Runs Trivy scans of the Dockerfiles and the two images.
   - **Run from:** App folder.
   - **Command:**
     ```bash
     bash scripts/scan_security.sh [--strict] [config|images]
     bash scripts/scan_security.sh --strict
     bash scripts/scan_security.sh config
     bash scripts/scan_security.sh images
     ```

3. **`scripts/update_lock.sh`**
   - **What it does:** Regenerates `requirements.lock` from `requirements.txt`.
   - **Run from:** App folder.
   - **Command:**
     ```bash
     bash scripts/update_lock.sh
     ```

4. **`scripts/seed_demo_data.sh`**
   - **What it does:** Creates demo users and sample shifts, tasks and delays through the API.
   - **Run from:** App folder.
   - **Command:**
     ```bash
     bash scripts/seed_demo_data.sh
     ```

5. **`e2e/cleanup-test-data.sql`**
   - **What it does:** Deletes the data a failed browser test left behind.
   - **Run from:** App folder.
   - **Command:** See Section 7.

6. **`npm test` and friends**
   - **What it does:** Runs browser tests (Playwright).
   - **Run from:** `e2e` folder.
   - **Command:** See Section 8.

7. **`docker compose ... alembic ...`**
   - **What it does:** Handles migration status and checks.
   - **Run from:** App folder.
   - **Command:** See Section 9.
---

## 3. `scripts/verify_stack.sh`

**What it does.** Asks the running stack "are you healthy?" at every layer and prints PASS or FAIL for each check. It does not stop at the first failure: it runs all checks so you see every problem at once. It ends with a summary line and an exit code.

**When to use it.** After starting or rebuilding the stack, after any change, before committing, and later as the first gate in the pipeline.

**Command:**

```bash
bash scripts/verify_stack.sh
echo "exit code: $?"
```

**Options.**

| Option   | Meaning                                                                      |
|----------|------------------------------------------------------------------------------|
| `--e2e`  | Also runs the browser tests (a 15th check). Needs the `e2e` folder installed |
| `--help` | Prints the usage lines                                                       |


### Settings (environment variables, all optional)

1. **`ENV_FILE`**
   - **Default:** `.env.docker`
   - **Meaning:** The settings file to read ports and the admin login from.

2. **`WAIT_SECONDS`**
   - **Default:** `60`
   - **Meaning:** How long to wait for containers that are still `starting`.

3. **`POLL_SECONDS`**
   - **Default:** `2`
   - **Meaning:** How often to look while waiting.

4. **`APP_PORT`, `WEB_PORT`**
   - **Default:** `8004`, `8080` (or the values in `.env.docker`).
   - **Meaning:** Where the API and web app listen.

### Expected output when everything is healthy

```text
Checking the stack (web http://localhost:8080, API http://localhost:8004) ...

Containers
[PASS] database container is healthy
[PASS] migration job finished with exit code 0
[PASS] API container is healthy
[PASS] web container is healthy

Web server and API
[PASS] web server answers its own health address
[PASS] API answers directly on port 8004
[PASS] API answers through the web server (proxy)

Database
[PASS] migrations are at the latest revision
[PASS] database matches the models (no drift)

Security
[PASS] API container does not run as root
[PASS] web container does not run as root

Reproducibility
[PASS] API image contains exactly the versions in requirements.lock

End to end
[PASS] admin can log in through the web server
[PASS] lookup values are served with that login

Result: 14 passed, 0 failed
```

The command takes about 15 seconds, mostly because the two migration checks start short-lived containers. If a container is still `starting` (right after a start), the script prints `Waiting for: crane-web (still starting, 2s of 60s)` lines and then continues.

### What each check proves

1. **Database container is healthy**
   - **What it proves:** PostgreSQL answers its own health check.

2. **Migration job finished with exit code 0**
   - **What it proves:** `crane-migrate` ran `alembic upgrade head` and stopped successfully.

3. **API container is healthy**
   - **What it proves:** The API answers its own health check.

4. **Web container is healthy**
   - **What it proves:** nginx answers its own health check.

5. **Web server answers its own health address**
   - **What it proves:** `GET /healthz` on port 8080 returns HTTP 200.

6. **API answers directly on port 8004**
   - **What it proves:** `GET /health` returns `{"status":"ok"}`.

7. **API answers through the web server (proxy)**
   - **What it proves:** The same answer is returned via port 8080, so the nginx proxy works.

8. **Migrations are at the latest revision**
   - **What it proves:** `alembic current` reports `(head)`.

9. **Database matches the models (no drift)**
   - **What it proves:** `alembic check` finds no difference between the tables and the code.

10. **API container does not run as root**
    - **What it proves:** `id -u` in the container is not `0`.

11. **Web container does not run as root**
    - **What it proves:** The same check confirms nginx is not running as root.

12. **API image contains exactly the versions in `requirements.lock`**
    - **What it proves:** `pip freeze` inside the image equals the lock file.

13. **Admin can log in through the web server**
    - **What it proves:** A real login through port 8080 returns a token.

14. **Lookup values are served with that login**
    - **What it proves:** The token works on a protected endpoint.

**Exit codes.**

| Code | Meaning                                                               |
|------|-----------------------------------------------------------------------|
| `0`  | Every check passed                                                    |
| `1`  | One or more checks failed (each failed line has a "what to try" hint) |
| `2`  | Docker itself is not reachable                                        |

**Practice: break it on purpose.** This is the quickest way to learn what the checks mean:

```bash
docker compose --env-file .env.docker stop crane-web
bash scripts/verify_stack.sh
echo "exit code: $?"
docker compose --env-file .env.docker start crane-web
bash scripts/verify_stack.sh
```

With the web container stopped you should see **8 passed and 6 failed** (web health, web `/healthz`, the proxy, web non-root, the login and the lookups) and `exit code: 1`. After the restart the script waits for `crane-web` and ends with `14 passed, 0 failed`.

### Troubleshooting

1. **Symptom:** `[FAIL] Docker is not reachable`
   - **Cause:** Docker Desktop is not running.
   - **Fix:** Start Docker Desktop and wait for "engine running".

2. **Symptom:** `web container is healthy` fails right after a restart.
   - **Cause:** The container is still starting.
   - **Fix:** The script waits 60 seconds; run it again.

3. **Symptom:** `API image contains exactly the versions in requirements.lock` fails.
   - **Cause:** The image is older than the lock file.
   - **Fix:** Rebuild the API image without using the cache, then start the stack:
     ```bash
     docker compose --env-file .env.docker build --no-cache crane-app
     docker compose --env-file .env.docker up -d --wait
     ```

4. **Symptom:** `admin can log in` fails.
   - **Cause:** Wrong `BOOTSTRAP_ADMIN_*` values in `.env.docker`, or the admin password was changed.
   - **Fix:** Check the file, or log in manually and read the API log.

5. **Symptom:** `failed to get console mode ...` lines appear in other output.
   - **Cause:** Harmless Docker message in Git Bash.
   - **Fix:** Ignore.
---

## 4. `scripts/scan_security.sh`

**What it does.** Runs **Trivy** (a free security scanner) as a container and checks (1) your Dockerfiles for risky settings and (2) your two built images for known vulnerabilities (CVEs). Details and how to react to findings are in `docs/PROJECT-PHASES/Phase-11.1-CONTAINER-SECURITY.md`.

**Command:**

```bash
bash scripts/scan_security.sh
echo "exit code: $?"
```

**Options.**

| Option     | Meaning                                                                      |
|------------|------------------------------------------------------------------------------|
| `config`   | Only scan the Dockerfiles (fast, about a minute the first time)              |
| `images`   | Only scan the two built images                                               |
| `--strict` | Exit with code 1 when serious findings exist. This is how a pipeline uses it |
| `--help`   | Prints the usage lines                                                       |

### Settings (optional)

1. **`SEVERITY`**
   - **Default:** `HIGH,CRITICAL`
   - **Meaning:** Which severities to report, for example `LOW,MEDIUM,HIGH,CRITICAL`.

2. **`TRIVY_IMAGE`**
   - **Default:** `aquasec/trivy:latest`
   - **Meaning:** Which Trivy container to run.

3. **`TRIVY_DB_REPOSITORY`**
   - **Default:** Trivy's default.
   - **Meaning:** A different host for the vulnerability database when the default is busy, for example `public.ecr.aws/aquasecurity/trivy-db`.

**How it works.** It starts the Trivy container with `docker run`. The image scan reads your images through the Docker socket; the Dockerfile scan reads your project folder. A Docker volume named `trivy-cache` keeps the downloaded vulnerability database, so only the first run is slow. Trivy ends with code `5` when it finds something (its own errors end with `1`), so the script can tell "found problems" from "could not scan".

**Expected output when everything is clean (shortened):**

```text
== Dockerfiles (risky settings), severity HIGH,CRITICAL
... Trivy report summary ...
[CLEAN]    Dockerfiles in this project

== Image mecandjeo-mhc-monitoring:dev (known vulnerabilities with a fix available), severity HIGH,CRITICAL
... Trivy report summary ...
[CLEAN]    mecandjeo-mhc-monitoring:dev

== Image mecandjeo-mhc-web:dev (known vulnerabilities with a fix available), severity HIGH,CRITICAL
... Trivy report summary ...
[CLEAN]    mecandjeo-mhc-web:dev

Result: 0 scan(s) with findings, 0 error(s)
```

A finding looks like `[FINDINGS] mecandjeo-mhc-monitoring:dev` with a table above it. How to read and fix it: `docs/PROJECT-PHASES/Phase-11.1-CONTAINER-SECURITY.md`, sections 8 and 9.

**Exit codes.**

| Code | Meaning                                                         |
|------|-----------------------------------------------------------------|
| `0` | No findings, or findings were shown but `--strict` was not used  |
| `1` | Findings exist and `--strict` was used                           |
| `2` | A scan could not run (Docker down, image not built, Trivy error) |

### Troubleshooting

1. **Symptom:** `[ERROR] ... (not built: run docker compose ... build)`
   - **Fix:**
     ```bash
     docker compose --env-file .env.docker build
     ```

2. **Symptom:** `TOOMANYREQUESTS` or `failed to download vulnerability DB`
   - **Fix:** Wait and retry, or set an alternative vulnerability database repository:
     ```bash
     export TRIVY_DB_REPOSITORY=public.ecr.aws/aquasecurity/trivy-db
     ```

3. **Symptom:** A path or mount error occurs during the Dockerfile scan.
   - **Fix:** Run the image scan mode and report the message:
     ```bash
     bash scripts/scan_security.sh images
     ```

---

## 5. `scripts/update_lock.sh`

**What it does.** Installs the packages listed in `requirements.txt` into a clean `python:3.12-slim` container and records the exact version of every installed package (including the ones those packages need) in `requirements.lock`. The Docker build installs from that lock, so every build gets exactly the same packages. Full explanation: `docs/PROJECT-PHASES/Phase-11.2-DEPENDENCY-LOCKING.md`.

**When to use it.** When you add, remove or change a line in `requirements.txt`, for a routine refresh, or when the scanner flags a Python package.

**Command:**

```bash
bash scripts/update_lock.sh
```

**Expected output (the number depends on the packages):**

```text
Installing the packages from requirements.txt into a clean python:3.12-slim container ...
Wrote requirements.lock with 25 pinned packages.
```

It takes about a minute. Then review the change and rebuild:

```bash
git diff requirements.lock
docker compose --env-file .env.docker build --no-cache crane-app
```

**Safety.** The result is written to a temporary file first. If the install fails, or the result lacks the main packages, the old `requirements.lock` is left untouched and the script says so.

**Exit codes.** `0` success, `1` the install or the sanity check failed (lock unchanged), `2` Docker not reachable or run from the wrong folder.

---

## 6. `scripts/seed_demo_data.sh`

**What it does.** Reads the admin login from `.env.docker`, signs in through the API, and creates demo accounts and sample work: `operator1`, `operator2` and `manager1` (all with the password `Securepass123!`), plus sample shifts, tasks and delays. Running it again is safe: existing items are reported as "already exists".

**Command:**

```bash
bash scripts/seed_demo_data.sh
```

**Expected output:** a line for each item created (or "already exists"), ending with `Done.`

**Use it** after the first start, and after `down -v` wiped the database. The demo accounts are for local use only.

---

## 7. `e2e/cleanup-test-data.sql`

**What it does.** Deletes the data that the browser test creates (a crane named `E2E-...`, users with `e2e-` email addresses, and their shifts, tasks and delays). A normal passing run cleans up after itself. A **failed** run stops before its cleanup and leaves these rows behind; this file removes them. It only touches rows named `E2E-` or `e2e-`.

**Command** (from the app folder):

```bash
docker compose --env-file .env.docker exec -T crane-db \
  sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < e2e/cleanup-test-data.sql
```

**Expected output:** `BEGIN`, a list of `DELETE n` lines, then `COMMIT`. Running it twice is harmless (the second time every count is `DELETE 0`).

**Check what is left (should show no rows or all inactive):**

```bash
docker compose --env-file .env.docker exec -T crane-db \
  sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA' <<'SQL'
select email, is_active from users where email like 'e2e-%' order by id;
select mhc_number, is_active from cranes where mhc_number like 'E2E-%' order by id;
select count(*) from shifts where status = 'active' and mhc_number like 'E2E-%';
SQL
```

---

## 8. The `e2e` npm scripts (browser tests)

Run these commands from the `e2e` folder, with the stack running.

The full guide is `docs/PROJECT-PHASES/Phase-11.4-PLAYWRIGHT-GUIDE.md`.

1. **`npm install`**
   - **What it does:** Installs Playwright (first time only).

2. **`npm run install:browser`**
   - **What it does:** Downloads the test browser (first time only).

3. **`npm test`**
   - **What it does:** Runs all browser tests without opening a window.
   - **Expected:** `6 passed`.

4. **`npm run test:headed`**
   - **What it does:** Runs the same tests in a visible browser window.

5. **`npm run test:ui`**
   - **What it does:** Opens an interactive window with a timeline of each step.
   - **Best for learning.**

6. **`npm run test:debug`**
   - **What it does:** Pauses at each step.

7. **`npm run codegen`**
   - **What it does:** Opens a browser and writes test code as you click.

8. **`npm run report`**
   - **What it does:** Opens the last run's HTML report.

9. **`npm run typecheck`**
   - **What it does:** Checks the test code for mistakes without running anything.

10. **`npx playwright test tests/login.spec.ts`**
    - **What it does:** Runs only one file.

11. **`npx playwright test -g "wrong password"`**
    - **What it does:** Runs only tests whose names contain the words.

---

## 9. Docker Compose and Alembic one-liners

All commands are run from the app folder.

1. **Start everything and wait until healthy**
   ```bash
   docker compose --env-file .env.docker up -d --build --wait
   ```

2. **Show all containers, including the finished migration job**
   ```bash
   docker compose --env-file .env.docker ps -a
   ```

3. **Rebuild one container only**
   ```bash
   docker compose --env-file .env.docker up -d --build --no-deps --wait crane-web
   ```

4. **Rebuild from scratch with the newest operating-system fixes**
   ```bash
   docker compose --env-file .env.docker build --pull --no-cache
   ```

5. **Check the Compose file is valid**
   - **Expected:** Prints nothing when valid.
   ```bash
   docker compose --env-file .env.docker config -q
   ```

6. **Check which migration the database is at**
   - **Expected:** `0001 (head)`.
   ```bash
   docker compose --env-file .env.docker run --rm --no-deps -T crane-migrate alembic current
   ```

7. **Check whether the models and database differ**
   - **Expected:** `No new upgrade operations detected.`
   ```bash
   docker compose --env-file .env.docker run --rm --no-deps -T crane-migrate alembic check
   ```

8. **Apply migrations by hand**
   ```bash
   docker compose --env-file .env.docker run --rm crane-migrate alembic upgrade head
   ```

9. **Check what is installed in the API image**
   ```bash
   docker compose --env-file .env.docker run --rm --no-deps -T crane-app pip freeze
   ```

10. **Check which user a container runs as**
    - **API expected:** `uid=999`.
    - **Web expected:** `uid=101`.
    ```bash
    docker compose --env-file .env.docker exec crane-app id
    docker compose --env-file .env.docker exec crane-web id
    ```

**Creating a new migration** is described step by step in `docs/PROJECT-PHASES/Phase-10.2-Database-Migrations-Explained.md`.


## 10. Exit code cheat sheet

1. **`verify_stack.sh`**
   - **Exit code 0:** All checks passed.
   - **Exit code 1:** A check failed.
   - **Exit code 2:** Docker is not reachable.

2. **`scan_security.sh`**
   - **Exit code 0:** Clean (or not strict).
   - **Exit code 1:** Findings with `--strict`.
   - **Exit code 2:** A scan could not run.

3. **`update_lock.sh`**
   - **Exit code 0:** Lock written.
   - **Exit code 1:** Install or check failed (lock unchanged).
   - **Exit code 2:** Docker is down or the wrong folder was used.

4. **Trivy itself (inside the script)**
   - **Exit code 0:** Clean.
   - **Exit code 1:** Trivy error.
   - **Exit code 5:** Findings (set by the script).

5. **`npm test` (Playwright)**
   - **Exit code 0:** All tests passed.
   - **Exit code 1:** A test failed.


## 11. How these become pipeline steps

In Phase 14 (GitHub Actions) the same commands run automatically on every change, in roughly this order:

| Pipeline step            | Command you already know                                                      |
|--------------------------|-------------------------------------------------------------------------------|
| Backend tests            | `pip install -r requirements-dev.txt`, then `python -m pytest tests -q`       |
| Frontend tests and build | `npm ci`, `npm run lint`, `npm run test`, `npm run build` (in `frontend`)     |
| Build the images         | `docker compose build`                                                        |
| Start the stack          | `docker compose up -d --wait`                                                 |
| Check the stack          | `bash scripts/verify_stack.sh`                                                |
| Browser tests            | `cd e2e && npm ci && npx playwright install --with-deps chromium && npm test` |
| Security gate            | `bash scripts/scan_security.sh --strict`                                      |

A pipeline stops at the first step whose exit code is not `0`, which is exactly why these scripts end with meaningful exit codes.
