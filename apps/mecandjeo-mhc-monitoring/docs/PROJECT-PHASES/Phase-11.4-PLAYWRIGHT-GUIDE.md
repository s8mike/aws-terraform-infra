<!-- PLAYWRIGHT-GUIDE.md: a standalone guide to the browser (end-to-end) tests in the e2e folder: what Playwright is, how to set it up and run it, what each test does, how to read results, how to write tests, and the questions asked while learning it. -->

# Playwright Browser Tests: Complete Guide

This guide explains the browser tests of the project: what they are, how to set them up and run them, how to read the results, what each test does, how to write your own, and how to clean up. It assumes no earlier experience with testing tools. A list of the questions asked while learning it, with answers, is at the end.

Commands are for **Git Bash**. The browser tests live in the `e2e` folder (short for "end to end").

## Contents

1. What Playwright is
2. How it differs from your manual checks and from the other tests
3. What is in the `e2e` folder
4. One-time setup
5. Running the tests
6. Reading the results
7. What the tests do
8. How a test is written
9. Learning tools: UI mode, codegen and debug
10. Writing your own test
11. Cleaning up leftover test data
12. Troubleshooting
13. Safety rules
14. Questions and answers
15. Where this goes next

---

## 1. What Playwright is

**Playwright** is a tool that drives a real web browser by program. Think of a robot colleague who opens Chrome, types into the login form, clicks the buttons, reads what appears on the screen, and tells you whether it matches what you expected.

In this project it opens a real Chrome against the **whole running system** (nginx, the API, the database and the migrations) and performs the journey you would otherwise perform by hand: sign in as an admin, create users, work a shift as an operator, check it as a manager, download a report.

The browser it uses is a separate copy that Playwright installs for itself (on Windows under `C:\Users\<you>\AppData\Local\ms-playwright`). It does not touch your everyday browser.

## 2. How it differs from your manual checks and from the other tests

It **does not replace** your manual checks or the other tests. It automates the repeatable parts, and each level proves something different.

1. **Manual browser checks**
   - **Who or what runs it:** You.
   - **Browser:** A real one.
   - **Backend and database:** Real.
   - **What it proves:** Look, feel, surprises.
   - **Speed:** Slow, varies.
   - **Repeatable:** No.

2. **Vitest (107 tests)**
   - **Who or what runs it:** A program.
   - **Browser:** A simulated one (jsdom).
   - **Backend and database:** Faked.
   - **What it proves:** One component or function behaves.
   - **Speed:** Seconds.
   - **Repeatable:** Yes.

3. **pytest (71 tests)**
   - **Who or what runs it:** A program.
   - **Browser:** None.
   - **Backend and database:** A temporary SQLite database.
   - **What it proves:** One API rule behaves.
   - **Speed:** About a minute.
   - **Repeatable:** Yes.

4. **Playwright (6 tests)**
   - **Who or what runs it:** A program.
   - **Browser:** A real one (Chromium).
   - **Backend and database:** **Real** — the whole Docker stack.
   - **What it proves:** The **whole journey** works end to end.
   - **Speed:** About 20 to 30 seconds.
   - **Repeatable:** Yes.

**Why manual checks still matter**

Your eyes are still needed for judgment calls such as colors, layout and readability.

Playwright checks that the system **works**; you check that it **looks right**.
---

## 3. What is in the `e2e` folder

1. **`package.json`**
   - **What it does:** Lists the tools (Playwright, TypeScript) and the commands (`npm test` and others).

2. **`package-lock.json`**
   - **What it does:** Records the exact versions of those tools (created by `npm install`; commit it).

3. **`tsconfig.json`**
   - **What it does:** Contains the settings for the TypeScript type checker (`npm run typecheck`).

4. **`.gitignore`**
   - **What it does:** Keeps `node_modules`, `test-results` and `playwright-report` out of Git.

5. **`playwright.config.ts`**
   - **What it does:** Defines where the stack is, what to record on failure, and which browser to use.

6. **`global-setup.ts`**
   - **What it does:** Runs once before the tests. Stops early with a clear message if the stack is not running or the admin password is unknown.

7. **`helpers/env.ts`**
   - **What it does:** Finds the admin login: environment variables first, then `.env.docker`.

8. **`helpers/ui.ts`**
   - **What it does:** Contains shared steps: sign in, sign out, and a short pause (`tickSecond`).

9. **`tests/login.spec.ts`**
   - **What it does:** Contains 4 tests about signing in and route protection.

10. **`tests/journey.spec.ts`**
    - **What it does:** Contains 1 long test covering the whole journey (section 7.2).

11. **`tests/something.spec.ts`**
    - **What it does:** Your own test (section 10): "the admin sees the Users tab first".

12. **`cleanup-test-data.sql`**
    - **What it does:** Removes data left behind by a failed run (section 11).


## Settings in `playwright.config.ts` worth knowing

1. **`baseURL`**
   - **Value:** `http://localhost:8080` (or `E2E_BASE_URL`).
   - **Meaning:** The web app to test.

2. **`workers: 1`, `fullyParallel: false`**
   - **Meaning:** Runs one test at a time because the journey changes shared data.

3. **`retries`**
   - **Value:** `0`.
   - **Meaning:** A failure is reported, not retried.

4. **`timeout`**
   - **Value:** 180 seconds per test.

5. **`expect.timeout`**
   - **Value:** 10 seconds.
   - **Meaning:** How long a check keeps retrying before it fails.

6. **`screenshot`**
   - **Value:** `only-on-failure`.
   - **Meaning:** A screenshot is saved only for failed tests.

7. **`trace`**
   - **Value:** `retain-on-failure`.
   - **Meaning:** A step-by-step recording is kept only for failed tests.

### Environment variables (all optional)

- `E2E_BASE_URL`
- `E2E_ADMIN_EMAIL`
- `E2E_ADMIN_PASSWORD`
---

## 4. One-time setup

Run from `apps/mecandjeo-mhc-monitoring/e2e`:

```bash
npm install
npm run install:browser
npm run typecheck
```

1. **`npm install`**
   - **What happens:** Installs Playwright and TypeScript.
   - **Expected:** `added 6 packages ... found 0 vulnerabilities`.

2. **`npm run install:browser`**
   - **What happens:** Downloads the test browser (about 120 MB, once).
   - **Expected:** A download progress bar, then "downloaded to ...ms-playwright...".

3. **`npm run typecheck`**
   - **What happens:** Checks the test code for mistakes without running it.
   - **Expected:** No output, then the prompt returns.

You need Node 20 or newer (the project uses Node 24) and about 1 GB of free disk space to be comfortable. The stack must be running before you run the tests:

```bash
cd ..
docker compose --env-file .env.docker up -d --wait
```

---

## 5. Running the tests

Run these commands from the `e2e` folder.

1. **`npm test`**
   - **What it does:** Runs all tests without opening a browser window.
   - **Expected:** `6 passed`.

2. **`npm run test:headed`**
   - **What it does:** Runs the same tests in a visible browser window so you can watch them.

3. **`npm run test:ui`**
   - **What it does:** Opens an interactive window with a timeline. Click any step to see the page at that moment.
   - **Best for learning.**

4. **`npm run test:debug`**
   - **What it does:** Pauses at each step so you can step through the test.

5. **`npm run codegen`**
   - **What it does:** Opens a browser and **writes test code as you click**.

6. **`npm run report`**
   - **What it does:** Opens the report of the last run.

7. **`npm run typecheck`**
   - **What it does:** Checks the test code without running it.

8. **`npx playwright test tests/login.spec.ts`**
   - **What it does:** Runs only one test file.

9. **`npx playwright test -g "wrong password"`**
   - **What it does:** Runs only tests whose names contain the words.

10. **`npm test -- --trace on`**
    - **What it does:** Records a step-by-step trace even for passing tests.

### Expected output of `npm test`


```text
Running 6 tests using 1 worker

  ok 1 [chromium] › tests\journey.spec.ts:35:5 › admin prepares users and a crane, an operator works a shift, a manager sees and downloads it (10.7s)
  ok 2 [chromium] › tests\login.spec.ts:7:7 › login and route protection › a signed-out visitor is sent to the login page (575ms)
  ok 3 ... › a wrong password shows a clear message and stays on the login page (1.1s)
  ok 4 ... › the eye button shows and hides the typed password (601ms)
  ok 5 ... › the admin can sign in, reaches the admin screen, and can sign out again (1.1s)
  ok 6 ... › tests\something.spec.ts:6:5 › the admin sees the Users tab first (748ms)

  6 passed (17.7s)
```

The count is 6 because the folder holds 4 login tests, 1 journey test and 1 test of your own. A different number simply means a different number of tests in `tests/`.

**When to run it:** after changing screens, the API, nginx, Docker or migrations; before you commit; and later, before every deployment.

---

## 6. Reading the results

`ok` means passed and `x` means failed. After the list, every failure prints its error and the exact line of the test that failed. Playwright prints failure details **after** the whole list, so scroll down.

### 6.1 The report

```bash
npm run report
```

Opens `e2e/playwright-report/index.html`. It is created on every run, passing or not. Click a test to see its steps, and for a failed test a **screenshot** and a **trace**.

### 6.2 Screenshots and traces

With the settings in `playwright.config.ts`, **a passing run takes no screenshots**: they are saved only for failed tests, so the results folder stays empty when all is well. To look at what a passing run did:

```bash
npm test -- --trace on
npm run report
```

Open a test in the report and use its **Traces** tab: a timeline of every step with a picture of the page at that moment. There is no command-line switch for plain screenshots. To keep them always, change `screenshot: 'only-on-failure'` to `screenshot: 'on'` in `playwright.config.ts` (they go to `e2e/test-results/`).

### 6.3 When a test fails: three questions

1. What does the error say, and on which line?
2. What does the screenshot (or the trace) show?
3. Is the **app** wrong, or is the **test** out of date? If you changed a button's wording, the test needs the new wording; if the app misbehaves, fix the app.

---

## 7. What the tests do

### 7.1 `tests/login.spec.ts` (4 tests)

1. **A signed-out visitor is sent to the login page**
   - **What it proves:** Opening `/manager` without signing in redirects to `/login` and shows the title.

2. **A wrong password shows a clear message and stays on the login page**
   - **What it proves:** The message "Invalid email or password" appears, and the URL stays `/login`.

3. **The eye button shows and hides the typed password**
   - **What it proves:** The password field changes between hidden and visible.

4. **The admin can sign in, reaches the admin screen, and can sign out again**
   - **What it proves:** A real login works end to end, and the Admin screen opens.

### 7.2 `tests/journey.spec.ts` (1 test in 6 steps)

The test creates its own data with unique names (a short time-based code such as `E2E-mvpp0u1o`), so repeated runs never collide. It only needs the bootstrap admin from `.env.docker`.

1. **Step 1 — Admin prepares**
   - **What it does:** Signs in as admin; adds a crane `E2E-...`; adds an operator and a manager.
   - **What it proves:** The admin screens work, and new accounts can be created.

2. **Step 2 — Operator starts**
   - **What it does:** Signs in as the operator; starts a shift on the new crane; starts a task (Discharging, Deck Free Bay, a vessel name).
   - **What it proves:** The new crane appears for operators; shifts and tasks start.

3. **Step 3 — A delay blocks the task**
   - **What it does:** Starts a delay (Awaiting Trucks); checks the red notice "End the active delay before ending the task." and that **End task** is disabled; ends the delay.
   - **What it proves:** The business rule that blocks ending a task during a delay.

4. **Step 4 — Operator ends the task**
   - **What it does:** Enters 12 containers and ends the task; checks "This shift" shows 1 completed task and 12 containers.
   - **What it proves:** Totals update correctly.

5. **Step 5 — Manager checks**
   - **What it does:** Signs in as the manager; sees the operator on shift; filters Reports by the crane; checks 1 task, 12 containers and the vessel; downloads `historical-performance.csv`.
   - **What it proves:** The manager's live overview, report and CSV download.

6. **Step 6 — Clean up**
   - **What it does:** The operator ends the shift; the admin deactivates both users and retires the crane.
   - **What it proves:** The test leaves nothing active behind.

### 7.3 `tests/something.spec.ts`

Your own test, written from the template in section 10.

---

## 8. How a test is written

Every test does three things, and your own tests show each one:

```ts
await page.getByLabel('Email').fill(adminEmail)              // 1. find a thing the way a person would, and act on it
await page.getByRole('button', { name: 'Sign in' }).click()  // 2. find it by what it says, and click
await expect(page).toHaveURL(/\/admin$/)                     // 3. check the result
```

### Finding things

1. **`getByLabel('Email')`**
   - **Finds:** A form field by its label.
   - **Example:** Text boxes and drop-downs.

2. **`getByRole('button', { name: 'Sign in' })`**
   - **Finds:** A button, heading, tab, table row or cell by role and name.
   - **Example:** Buttons, `heading`, `tab`, `row`, `cell`.

3. **`getByText('...')`**
   - **Finds:** Plain text on the page.
   - **Example:** A notice message.

4. **`locator('.card')`**
   - **Finds:** A CSS selector (last resort).
   - **Example:** The summary cards.

**Actions:** `fill('text')` types, `click()` clicks, `selectOption({ label: '...' })` chooses from a drop-down.

**Checks (`expect`).** They **retry automatically** for up to 10 seconds, so the test needs no manual pauses: `toBeVisible()`, `toBeHidden()`, `toHaveText()`, `toContainText()`, `toHaveURL()`, `toBeDisabled()`.

**Strict mode.** If your description matches more than one element, Playwright stops with a `strict mode violation` instead of guessing. The cure is a more specific description. This happened in this project: the first journey run failed because the operator's name appears in **two tables** on the manager overview ("Operators on shift" and "Open shifts"), so the test looked for the row inside the right block only.

**`test.step`** groups actions under a name, so the report reads like the list in 7.2.

**Pauses.** The app records times to the second, and an end time must be later than its start. `tickSecond()` in `helpers/ui.ts` waits 1.1 seconds before ending something just started. It is the only deliberate pause.

**Browser dialogs.** The app asks for confirmation with the browser's own dialog (for example "Deactivate ...?"). The journey accepts them automatically with `page.on('dialog', ...)`.

---

## 9. Learning tools: UI mode, codegen and debug

1. **UI mode**
   - **Command:** `npm run test:ui`
   - **What to do:** Press the play button on a test. Click any step in the timeline to see the page at that moment and its locators.

2. **Codegen**
   - **Command:** `npm run codegen`
   - **What to do:** A browser and an inspector open. Click through the app; code appears. Copy it into a new test.

3. **Debug**
   - **Command:** `npm run test:debug`
   - **What to do:** Step through a test one action at a time.

4. **Headed**
   - **Command:** `npm run test:headed`
   - **What to do:** Watch the real browser work.

**Important:** Recorded code from `codegen` is a starting point. Give the test a clear name and replace guessed data with unique names.
---

## 10. Writing your own test

Create `e2e/tests/something.spec.ts` (or any `*.spec.ts` file):

```ts
// What this test proves, in one line.
import { expect, test } from '@playwright/test'
import { adminEmail, adminPassword } from '../helpers/env'
import { signIn } from '../helpers/ui'

test('the admin sees the Users tab first', async ({ page }) => {
  await signIn(page, adminEmail, adminPassword ?? '', /\/admin$/)
  await expect(page.getByRole('heading', { name: 'Users' })).toBeVisible()
})
```

Rules of thumb:

- Start with one clear sentence of what the test proves.
- Make the test **independent**: it should not rely on another test having run.
- If it creates data, give it a unique name starting with `E2E` or `e2e-`, and clean up (section 11).
- Prefer `getByLabel`, `getByRole` and `getByText` over CSS selectors.
- Run it alone while writing: `npx playwright test tests/something.spec.ts`.
- When you change a screen's wording, update the tests that mention it.

---

## 11. Cleaning up leftover test data

A passing run cleans up after itself. A **failed** run stops before its cleanup and leaves an active `E2E-...` crane, two `e2e-...` users and possibly an open shift. An open shift would show up on the manager's live overview.

The file `cleanup-test-data.sql` removes everything named `E2E-` or `e2e-`. From `apps/mecandjeo-mhc-monitoring`:

```bash
docker compose --env-file .env.docker exec -T crane-db \
  sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < e2e/cleanup-test-data.sql
```

Expected: `BEGIN`, a list of `DELETE n` lines, `COMMIT`. It is safe to run twice. Check afterwards:

```bash
docker compose --env-file .env.docker exec -T crane-db \
  sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA' <<'SQL'
select email, is_active from users where email like 'e2e-%' order by id;
select mhc_number, is_active from cranes where mhc_number like 'E2E-%' order by id;
select count(*) from shifts where status = 'active' and mhc_number like 'E2E-%';
SQL
```

Expected after cleanup: no user rows, no crane rows, and `0`. After a **passing** run you will see the test users and crane with `f` (inactive), because the journey retires them rather than deleting them.

---

## 12. Troubleshooting

1. **Symptom:** `The stack is not answering at http://localhost:8080/health`
   - **Cause:** The stack is not running.
   - **Fix:**
     ```bash
     docker compose --env-file .env.docker up -d --wait
     ```

2. **Symptom:** `The admin password was not found`
   - **Cause:** `.env.docker` could not be read.
   - **Fix:** Set `E2E_ADMIN_PASSWORD`, or run from the `e2e` folder.

3. **Symptom:** `Executable doesn't exist ...`
   - **Cause:** The browser is not installed.
   - **Fix:**
     ```bash
     npm run install:browser
     ```

4. **Symptom:** `strict mode violation: ... resolved to 2 elements`
   - **Cause:** A description matched more than one element.
   - **Fix:** Make it more specific (add a name, scope it to a block).

5. **Symptom:** `Timeout ... waiting for ...`
   - **Cause:** An element never appeared.
   - **Fix:** Open the screenshot or trace. Check whether the screen is different from what the test expects.

6. **Symptom:** A step fails right after an end action with "ended_at must be after started_at" on screen.
   - **Cause:** A pause was too short.
   - **Fix:** The one-second margin in `tickSecond()`; tell whoever maintains the tests.

7. **Symptom:** Only some tests were found.
   - **Cause:** Test files must end in `.spec.ts` and live in `tests/`.
   - **Fix:** Rename or move the file.

8. **Symptom:** The report is empty.
   - **Cause:** `npm test` has not run yet.
   - **Fix:** Run it, then:
     ```bash
     npm run report
     ```

9. **Symptom:** Leftover `E2E` data after a failure.
   - **Cause:** Cleanup was skipped.
   - **Fix:** See Section 11.
---

## 13. Safety rules

- These tests **create and change real data** in whichever stack they point at. Run them only against your **local** stack.
- Never set `E2E_BASE_URL` to a real, shared or production address.
- Test data always starts with `E2E` or `e2e-`, so it is easy to find and remove.
- Never put real passwords in test files. The admin password comes from `.env.docker`, which is not committed.

---

## 14. Questions and answers

**What is Playwright, and what is the test about?** A tool that drives a real browser. The test performs the whole journey (admin, operator, manager) against the full stack and checks the results (section 7).

**Does it override the regular browser test I do by hand? What is the difference?** No. It automates the repeatable checks so they run the same way every time in under a minute. Your own checks remain for judgment calls such as look and feel (section 2).

**Is 298 GB of free disk enough?** Far more than enough. The browser download is about 120 MB, once.

**Why did 6 tests run when 5 were given?** The sixth is your own `something.spec.ts`. Playwright runs every `*.spec.ts` file in `tests/`.

**Why were no screenshots produced when the tests passed?** By design: `screenshot: 'only-on-failure'`. To see what a passing run did, use `npm test -- --trace on` and the report's Traces tab, or set `screenshot: 'on'` (section 6.2).

**What is a "strict mode violation"?** The description matched more than one element, and Playwright refuses to guess. It caused the first journey failure (section 8).

**Why does the first journey run fail with only a couple of lines on screen?** Playwright prints failure details after the pass and fail list; scroll down to the section beginning `1)`, or open the report.

**Why does the test pause for 1.1 seconds?** Times are recorded to the second and an end must be later than a start (section 8).

**Why does the test create its own users and crane?** So it needs nothing but the admin login, never collides with your demo data, and its data is easy to recognize and remove.

**What if a run fails halfway?** Cleanup is skipped; use `cleanup-test-data.sql` (section 11).

**Does Playwright replace Vitest or pytest?** No. They are faster and pinpoint a broken rule; Playwright is slower and proves the pieces work together.

**Can I point it at the cloud later?** Technically yes, with `E2E_BASE_URL`, but it creates real data, so only against a dedicated test environment, never production (section 13).

**Is the browser it installs used for my normal browsing?** No. It is a separate copy used only by Playwright.

---

## 15. Where this goes next

In Phase 14 the same tests run in GitHub Actions after the stack is started, with `npm ci`, `npx playwright install --with-deps chromium` and `npm test`. A failing journey then stops a deployment before it reaches the cloud, and the report and traces are kept as downloadable files of the run.
