<!-- TESTING-GUIDE.md: one page that compares every level of checking in the project (backend tests, frontend tests, browser tests, stack checks and security scans), with commands, expected results and when to run each. -->

# Testing and Checking Guide

This page ties together everything that checks the project: three levels of automated tests, plus two operational checks. For each one you will find what it proves, how to run it, the result you should see, and when to run it. It assumes no earlier experience.

Commands are for **Git Bash**. Run them from `apps/mecandjeo-mhc-monitoring` unless a row says another folder.

## Contents

1. The big picture
2. Backend tests (pytest)
3. Frontend tests (Vitest)
4. Browser tests (Playwright)
5. Stack check and security scan
6. Tests, checks and scans compared
7. When to run what
8. The order a pipeline will use
9. What is not covered yet
10. Common questions

---

## 1. The big picture

Each kind of check answers a different question. The cheap, fast ones catch most mistakes; the slower, broader ones prove the pieces work together.

### Testing levels

1. **Level 1 — Backend rules**
   - **Tool:** `pytest`
   - **Count:** 71 tests in 12 files.
   - **Question it answers:** Does each API rule behave?
   - **Speed:** About 1 minute.
   - `python -m pytest tests -q`


2. **Level 2 — Screens and logic**
   - **Tool:** `Vitest`
   - **Count:** 107 tests in 16 files.
   - **Question it answers:** Does each component and function behave?
   - **Speed:** About 30 seconds.
   - `npm run test`


3. **Level 3 — Whole journey**
   - **Tool:** `Playwright` 
   - **Count:** 6 tests.
   - **Question it answers:** Does the **running system** work in a real browser?
   - **Speed:** About 20 to 30 seconds.
   - `cd e2e && npm test`

4. **Level 4 — Stack health**
   - **Tool:** `scripts/verify_stack.sh`
   - **Count:** 14 checks.
   - **Question it answers:** Is the running stack healthy, secure, and reproducible?
   - **Speed:** About 15 seconds.

5. **Level 5 — Security**
   - **Tool:** `scripts/scan_security.sh`
   - **Count:** 3 scans.
   - **Question it answers:** Do the Dockerfiles and images contain known flaws?
   - **Speed:** Seconds (after the first run).

### Important distinction

None of these levels replaces another.

- A failing Level 1 test points at one specific rule.
- A failing Level 3 test tells you that something is broken somewhere along the path through the running system.

---

## 2. Backend tests (pytest)

**What they are.** Python tests for the API. They run on your computer (not in Docker) against a **temporary SQLite database**, so they never touch your PostgreSQL data.

**One-time setup:**

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements-dev.txt
```

`requirements-dev.txt` installs the exact locked package versions that the container uses, plus `pytest` and `httpx`.

**Run:**

```bash
python -m pytest tests -q
```

Expected last line:

```text
71 passed, 1 warning in 66.22s (0:01:06)
```

The warning is a harmless notice from a library (`httpx`).

**Every new terminal needs the environment activated first.** If `pytest` says `ModuleNotFoundError: No module named 'fastapi'`, the virtual environment is not active in that terminal. Run `source .venv/Scripts/activate` (or `source venv/Scripts/activate`), check that the prompt starts with the environment name, and run the tests again. Check which Python you are using with `which python`.

| Variation                     | Command                                     |
|-------------------------------|---------------------------------------------|
| One line per test             | `python -m pytest tests -v`                 |
| One file                      | `python -m pytest tests/test_lookups.py -v` |
| Tests with a word in the name | `python -m pytest tests -k "password" -v`   |
| Stop at the first failure     | `python -m pytest tests -x`                 |

**What the 71 cover.** Health, authentication and roles, reference data and lookups, cranes, shifts, tasks and delays, change of password, operator workflow, reporting, the bootstrap, and (Phase 11) migrations and start-up behavior. Each file is explained in `docs/1. LOCAL-DEVELOPMENT.md`, section 11.

**Phase 11 tests**

1. **`tests/test_migrations.py`**
   - **Tests:** 6.
   - **Covers:** Verifies that migrations build the same schema as the models, can be undone, are safe to repeat, have a single head, can adopt an old database, and refuse an unstamped one.

2. **`tests/test_lifespan.py`**
   - **Tests:** 4.
   - **Covers:** Verifies that start-up creates tables and runs the bootstrap only as the two settings direct.
---

## 3. Frontend tests (Vitest)

**What they are.** Tests of the React code that run in a **simulated browser**. They check single components (forms, panels, tables) and functions (time handling, API calls) with the network faked.

### Run frontend tests

Run the following commands from the project root:

```bash
cd frontend
npm run test
```

**Expected result:** `16 passed` test files and `107 passed` tests.

### Frontend test commands

Run these commands from the `frontend` folder.

1. **Run all tests**
   ```bash
   npm run test
   ```

2. **Run tests for one area**
   ```bash
   npm run test:utils
   npm run test:api
   npm run test:theme
   npm run test:components
   npm run test:operator
   npm run test:admin
   npm run test:auth
   npm run test:pages
   ```

3. **Run tests in the folder you are currently in**
   ```bash
   npm run test:here
   ```

4. **Run tests in watch mode (re-runs on save)**
   ```bash
   npm run test:watch
   ```

### Additional frontend checks

After running the tests, also run:

1. **Lint**
   ```bash
   npm run lint
   ```
   - **Expected result:** 0 warnings and 0 errors.

2. **Build**
   ```bash
   npm run build
   ```
   - **Purpose:** Type-checks everything, including the tests.

**Further reading:** See `docs/PROJECT-PHASES/Phase-10.1-Frontend-Development.md`, sections 6 and 9, for details and explanations of every test.
---

## 4. Browser tests (Playwright)

**What they are.** A real Chrome, driven by a program, against the **full running Docker stack**: nginx, the API, PostgreSQL and the migrations. One long test performs the whole admin, operator and manager journey; four small tests cover sign-in.

**Run** with the stack up, from the `e2e` folder:

```bash
cd ../e2e            # or: cd e2e  from the app folder
npm test
```

Expected: `6 passed` in about 20 to 30 seconds.

The complete guide (setup, every command, reading reports, writing tests, cleanup) is `docs/PROJECT-PHASES/Phase-11.4-PLAYWRIGHT-GUIDE.md`.

---

## 5. Stack check and security scan

These are not tests of code. They check the **running stack and the built images**.

### 5.1 `bash scripts/verify_stack.sh`

Fourteen checks: containers healthy, migration job finished, web and API answering (directly and through the proxy), migrations at the latest revision with no drift, containers not running as root, the image matching `requirements.lock`, and a real login with a protected request.

Expected: `Result: 14 passed, 0 failed`, exit code 0. Add `--e2e` to include the browser tests as a 15th check. Details: `docs/PROJECT-PHASES/Phase-11.5-SCRIPTS-REFERENCE.md`, section 3.

### 5.2 `bash scripts/scan_security.sh`

Trivy scans of the Dockerfiles and both images. Expected: `[CLEAN]` three times and `Result: 0 scan(s) with findings, 0 error(s)`. With `--strict` the exit code is 1 when anything serious is found. Details: `docs/PROJECT-PHASES/Phase-11.1-CONTAINER-SECURITY.md`.

---

## 6. Tests, checks and scans compared

1. **Tests**
   - **Example:** pytest, Vitest, Playwright.
   - **Looks at:** Behaviour of code or of the whole system.
   - **Needs the stack running:** Only Playwright.
   - **Result changes when:** You change code.

2. **Checks**
   - **Example:** `verify_stack.sh`.
   - **Looks at:** The state of the running environment.
   - **Needs the stack running:** Yes.
   - **Result changes when:** You change configuration or something breaks.

3. **Scans**
   - **Example:** `scan_security.sh`.
   - **Looks at:** The contents of the images and Dockerfiles.
   - **Needs the stack running:** No (needs images built).
   - **Result changes when:** A new flaw is published, **even if nothing changed**.

**Why repeated scans matter:** A scan that passed last week can fail today without any change from you.

---

## 7. When to run what

1. **You changed a backend rule or route**
   - **Run:**
     ```bash
     python -m pytest tests -q
     ```

2. **You changed a migration or a model**
   - **Run:**
     ```bash
     python -m pytest tests -q
     bash scripts/verify_stack.sh
     ```

3. **You changed a frontend component or function**
   - **Run from the `frontend` folder:**
     ```bash
     npm run test
     npm run lint
     npm run build
     ```

4. **You changed a screen's wording or layout**
   - **Run:** The frontend tests, then:
     ```bash
     cd e2e
     npm test
     ```
   - **Why:** Tests find things by their text.

5. **You changed nginx, a Dockerfile or `docker-compose.yml`**
   - **Run:**
     ```bash
     docker compose --env-file .env.docker up -d --build --wait
     bash scripts/verify_stack.sh
     cd e2e
     npm test
     ```

6. **You changed `requirements.txt`**
   - **Run:** Update the lock file, rebuild, then run pytest, `verify_stack.sh` and `scan_security.sh --strict`.
   - **Commands:**
     ```bash
     bash scripts/update_lock.sh
     docker compose --env-file .env.docker up -d --build --wait
     python -m pytest tests -q
     bash scripts/verify_stack.sh
     bash scripts/scan_security.sh --strict
     ```

7. **Nothing changed, but a week has passed**
   - **Run:**
     ```bash
     bash scripts/scan_security.sh
     ```
   - **Why:** New flaws appear without any change.

8. **Before committing**
   - **Run:**
     ```bash
     python -m pytest tests -q
     cd frontend
     npm run test
     npm run lint
     npm run build
     cd ..
     bash scripts/verify_stack.sh
     cd e2e
     npm test
     cd ..
     bash scripts/scan_security.sh --strict
     ```

---

## 8. The order a pipeline will use

In Phase 14 (GitHub Actions), the same checks run automatically, starting with the cheapest and stopping at the first failure.

1. **Step 1 — Backend tests**
   - **Commands:**
     ```bash
     pip install -r requirements-dev.txt
     python -m pytest tests -q
     ```

2. **Step 2 — Frontend lint, tests and build**
   - **Commands:**
     ```bash
     npm ci
     npm run lint
     npm run test
     npm run build
     ```

3. **Step 3 — Build the images**
   - **Command:**
     ```bash
     docker compose build
     ```

4. **Step 4 — Start the stack**
   - **Command:**
     ```bash
     docker compose up -d --wait
     ```

5. **Step 5 — Stack check**
   - **Command:**
     ```bash
     bash scripts/verify_stack.sh
     ```

6. **Step 6 — Browser tests**
   - **Commands:**
     ```bash
     cd e2e
     npm ci
     npx playwright install --with-deps chromium
     npm test
     ```

7. **Step 7 — Security gate**
   - **Command:**
     ```bash
     bash scripts/scan_security.sh --strict
     ```

**Important:** The pipeline reads each step's **exit code** (`0` means success). This is why the scripts end with meaningful exit codes.

---

## 9. What is not covered yet

1. **No tests against PostgreSQL directly**
   - **Note:** Backend tests use SQLite; PostgreSQL is exercised by the browser tests and the stack check.

2. **The browser tests cover one main journey**
   - **Note:** Other roles' screens are covered by the Vitest component tests, not end to end.

3. **No test of two people using the system at once**
   - **Note:** Not planned for the local phase.

4. **No automatic cleanup after a failed browser run**
   - **Note:** Use `e2e/cleanup-test-data.sql`.

5. **No secret scanning of the code folder**
   - **Note:** A possible later addition to the scan script.

6. **No load or performance tests**
   - **Note:** Out of scope for the local phase.
---

## 10. Common questions

**Does a passing browser test make the unit tests unnecessary?** No. Unit tests are faster and point at the exact broken rule.

**Why are there so many kinds of checks?** Each is cheap at its own job. A rule is best checked in milliseconds by pytest; whether the proxy, the database and the screens agree is only visible end to end.

**The scan passed yesterday and fails today. Did I break something?** Not necessarily: new flaws are published daily (`docs/PROJECT-PHASES/Phase-11.1-CONTAINER-SECURITY.md`, section 9).

**Do I need Docker for the tests?** Backend and frontend tests: no. Browser tests, the stack check and the scan: yes.

**How long does the full set take?** Roughly 3 to 4 minutes in total: pytest 1 minute, Vitest 30 seconds, stack check 15 seconds, browser tests 30 seconds, scan under a minute.
