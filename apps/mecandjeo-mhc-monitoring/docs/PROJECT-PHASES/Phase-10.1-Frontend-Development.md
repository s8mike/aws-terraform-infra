# Frontend Development Guide

This guide takes you from a fresh checkout to the running web app, then shows how to build it, check it and test it. It assumes no earlier experience with React, Node or Vitest. A map of every folder and file is in `docs/7. Frontend-Structure.md`.

Commands are for **Git Bash** (the terminal that comes with Git for Windows). Lines starting with `#` are comments, so you can paste them along with the commands.

## Contents

1. What the frontend is
2. Before you start
3. Step by step: run the frontend
4. The screens and who can open them
5. All npm commands
6. Running the tests (everything, by folder, one file)
7. How the frontend talks to the backend
8. Things to know while using it
9. Understanding the tests
10. How this project was created (reference)
11. Troubleshooting
12. Phase 10 verification checklist

---

## 1. What the frontend is

A web application written in **React** and **TypeScript**, built and served by **Vite**. It has four parts: a login screen, an operator screen (shifts, tasks, delays, conditions), a manager screen (live overview, delays, performance, reports) and an admin screen (users, cranes, reference data).

It does not store data itself. Every action is a request to the backend API at `http://localhost:8004`, which writes to PostgreSQL. In development you open the app at `http://localhost:5173`.

| Piece      | Version used                                      |
|------------|---------------------------------------------------|
| Node.js    | 24.14.0 (needs 20.19 or newer, or 22.12 or newer) |
| npm        | 11.9.0                                            |
| Vite       | 8.3.x                                             |
| React      | 19                                                |
| TypeScript | 6                                                 |
| Vitest     | 5 (tests)                                         |

## 2. Before you start

You need three things on your computer.

| Tool                       | Why                           | Check              |
|----------------------------|-------------------------------|--------------------|
| Git for Windows (Git Bash) | Terminal and source control   | `git --version`    |
| Node.js 20.19+ or 22.12+   | Runs the build tools          | `node --version`   |
| Docker Desktop             | Runs the backend and database | `docker --version` |

Install Node from the LTS download on nodejs.org if `node --version` is older or missing, then close and reopen Git Bash. The backend must be set up first. If you have not done that, follow `docs/1. LOCAL-DEVELOPMENT.md` up to the section "Check that it is healthy".

## 3. Step by step: run the frontend

**Step 1. Open the frontend folder.** Replace the path with where you cloned the repository.

```bash
cd /c/Users/Home/Documents/MY-DEVOPS-WORKS/PROJECTS/vpc-aws-terraform-infra
cd apps/mecandjeo-mhc-monitoring/frontend
pwd
ls
```

You should see `package.json`, `vite.config.ts`, `index.html` and the folders `src` and `public`.

**Step 2. Check Node and npm.**

```bash
node --version
npm --version
```

Expected: `v20.19` or newer (for example `v24.14.0`) and an npm version number.

**Step 3. Install the packages.** This reads `package.json` and creates the `node_modules` folder. It takes about a minute the first time and only needs repeating when `package.json` changes.

```bash
npm install
```

Expected: a summary ending in `found 0 vulnerabilities`. Use `npm ci` instead if you want exactly the versions in `package-lock.json`.

**Step 4. Start the backend.** Open a second Git Bash window, go to `apps/mecandjeo-mhc-monitoring` (one folder up from `frontend`) and run:

```bash
docker compose --env-file .env.docker up -d
docker compose --env-file .env.docker ps
curl http://localhost:8004/health
```

Expected: both containers `(healthy)` and `{"status":"ok"}`. Wait about 20 seconds after starting if they are not healthy yet.

**Step 5. Load demo data (recommended).** In that same window, from `apps/mecandjeo-mhc-monitoring`:

```bash
bash scripts/seed_demo_data.sh
```

It creates `operator1`, `operator2` and `manager1`, with three completed tasks and one operator still working. It prints `Done.` at the end. If it says `operator1 already exists`, the demo data is already there and you can skip this step.

**Step 6. Start the frontend.** Back in the `frontend` window:

```bash
npm run dev
```

Expected:

```
  VITE v8.3.3  ready in 290 ms

  ➜  Local:   http://localhost:5173/
```

Leave this window open while you work. Vite reloads the page by itself whenever you save a file.

**Step 7. Check the link to the backend.** In any Git Bash window:

```bash
curl http://localhost:5173/health
```

Expected: `{"status":"ok"}`. That answer came from the backend, through the dev server, so the connection works.

**Step 8. Open the app and sign in.** Go to `http://localhost:5173` in your browser. You are sent to the login page.

| Account  | Email                                                 | Password                                |
|----------|-------------------------------------------------------|-----------------------------------------|
| Admin    | the value of `BOOTSTRAP_ADMIN_EMAIL` in `.env.docker` | the value of `BOOTSTRAP_ADMIN_PASSWORD` |
| Manager  | `manager1@example.com`                                | `Securepass123!`                        |
| Operator | `operator1@example.com`                               | `Securepass123!`                        |
| Operator | `operator2@example.com`                               | `Securepass123!`                        |

The demo accounts exist only after Step 5. Use the eye button in the password field to check what you typed.

**Step 9. Stop everything when you finish.** Press `Ctrl+C` in the frontend window. To pause the backend without losing data, run this from `apps/mecandjeo-mhc-monitoring`:

```bash
docker compose --env-file .env.docker stop
```

## 4. The screens and who can open them

| Address     | Who can open it     | What it does                                               |
|-------------|---------------------|------------------------------------------------------------|
| `/login`    | Everyone            | Sign in; a signed-in user is sent to their home page       |
| `/operator` | Operators           | Start and end a shift, tasks and delays; record conditions |
| `/manager`  | Managers and admins | Overview, delays, performance, reports with CSV download   |
| `/admin`    | Admins              | Users, cranes (MHC) and reference data                     |

Anyone who opens a page they are not allowed to see is sent to their own home page. Admins see header links to the manager view and the admin screen. Every signed-in user has a **theme** dropdown and a **Change password** button in the header.

## 5. All npm commands

Run these from the `frontend` folder.

| Command                   | What it does                                               |
|---------------------------|------------------------------------------------------------|
| `npm run dev`             | Starts the app at `http://localhost:5173` with auto-reload |
| `npm run build`           | Type-checks all code (tests included) and builds `dist/`   |
| `npm run lint`            | Checks the code for common mistakes                        |
| `npm run preview`         | Serves the built `dist/` locally                           |
| `npm run test`            | Runs all 107 tests once                                    |
| `npm run test:watch`      | Re-runs tests automatically as you edit                    |
| `npm run test:utils`      | Tests in `src/utils`                                       |
| `npm run test:api`        | Tests in `src/api`                                         |
| `npm run test:theme`      | Tests in `src/theme`                                       |
| `npm run test:components` | Tests in `src/components` (all subfolders)                 |
| `npm run test:operator`   | Tests in `src/components/operator`                         |
| `npm run test:admin`      | Tests in `src/components/admin`                            |
| `npm run test:auth`       | Tests in `src/auth`                                        |
| `npm run test:pages`      | Tests in `src/pages`                                       |
| `npm run test:here`       | Tests of the folder you are standing in                    |

## 6. Running the tests

### 6.1 Everything

```bash
npm run test
```

Expected:

```
 Test Files  16 passed (16)
      Tests  107 passed (107)
```

It takes about 30 seconds. Most of that is starting a simulated browser for each test file. The "jsdom was created 16 times" tip at the end is information, not a problem.

### 6.2 One folder at a time

Run these from the `frontend` folder.

| Command                   | Test files | Tests |
|---------------------------|------------|-------|
| `npm run test:utils`      |     3      |  21   |
| `npm run test:api`        |     2      |  19   |
| `npm run test:theme`      |     1      |  6    |
| `npm run test:components` |     8      |  49   |
| `npm run test:operator`   |     3      |  22   |
| `npm run test:admin`      |     2      |  12   |
| `npm run test:auth`       |     1      |  6    |
| `npm run test:pages`      |     1      |  6    |

`test:components` includes everything under `components`, so its 49 tests are the 22 operator tests, the 12 admin tests and 15 more in the folder itself.

### 6.3 From inside a folder

Go into any folder under `src` and run `test:here`. It runs only the tests of that folder, including its subfolders.

```bash
cd src/utils
npm run test:here
```

```bash
cd src/components/operator
npm run test:here
```

Expected for the first: `Test Files  3 passed (3)` and `Tests  21 passed (21)`. From the `frontend` folder itself, `test:here` runs everything. In a folder with no tests it prints `No test files found`; move to a folder that has tests.

### 6.4 One file, or tests by name

The `--` passes the rest of the line to the test runner.

```bash
npm run test -- src/utils/validation.test.ts
npm run test -- -t "password"
```

The first runs one file (11 tests). The second runs every test whose name contains the word `password`, in all files.

### 6.5 Watch mode

```bash
npm run test:watch
```

Press `q` to quit. The tests re-run each time you save a file.

## 7. How the frontend talks to the backend

The browser only ever talks to `http://localhost:5173`. The dev server forwards any request that starts with `/api` or `/health` to the backend at `http://localhost:8004`. The setting is in `vite.config.ts`:

```ts
server: {
  port: 5173,
  proxy: {
    '/api': 'http://localhost:8004',
    '/health': 'http://localhost:8004',
  },
},
```

Because everything looks like one site to the browser, no CORS settings are needed. Vite restarts by itself if you change this file. If the backend runs on another port, change both addresses.

## 8. Things to know while using it

**Purpose:** Use this guide to understand how sign-in, sessions, time handling, themes and automatic updates work, so you can use the application confidently and avoid common mistakes.

1. **Sign-in**
   - **How it works:** The token is stored in the browser tab (`sessionStorage`). Closing the tab signs you out. Tokens last 24 hours by default.

2. **Expired sessions**
   - **How it works:** Any "not signed in" response from the API sends you back to the login page.

3. **Wrong current password**
   - **How it works:** Changing a password with the wrong current password shows a red message and keeps you signed in.

4. **Times**
   - **How it works:** The app handles times in UTC internally and displays them in your local time.

5. **Trailing slashes**
   - **How it works:** Some API paths end in `/`, such as `/api/cranes/`. The code already uses the exact paths.

6. **Theme**
   - **How it works:** Choose Soft Color, Light, Grey or Dark. The selection is saved per user in this browser only.

7. **Live data**
   - **How it works:** The manager overview refreshes automatically every 15 seconds.

8. **Locked fields**
   - **How it works:** Clicking a locked reference-data code displays a red explanation.

## 9. Understanding the tests

### 9.1 What the test tools are

| Word            | Meaning                                                                       |
|-----------------|-------------------------------------------------------------------------------|
| Vitest          | The program that finds and runs the test files                                |
| jsdom           | A simulated browser, so React screens can be tested without opening one       |
| Testing Library | Finds things on a screen the way a person would (by label, button name, text) |
| `userEvent`     | Types, clicks and tabs like a real user                                       |
| `vi.mock(...)`  | Replaces a module (for example the API calls) with a fake for one test file   |
| `vi.fn()`       | A fake function that records how it was called                                |
| `expect(...)`   | Checks a result; the test fails if the check is false                         |

Every test follows the same pattern: arrange something on a screen or in a function, do what a user would do, then check the outcome. The API is always faked, so the tests need no backend and never change real data.

`src/test/setup.ts` runs before every test file and clears saved tokens, themes and rendered screens after each test, so tests cannot affect each other.

### 9.2 Test files in detail

**107 tests in 16 files.**

#### `src/utils/validation.test.ts` (11 tests): the password rules

1. **Empty password**
   - **Test:** Lists five rules, none met for an empty password.
   - **Sign:** The password field is empty.
   - **Proof:** Confirms the checklist has five rules and starts all red.

2. **Independent rule evaluation**
   - **Test:** Evaluates each rule independently.
   - **Sign:** The password meets one requirement at a time.
   - **Proof:** Confirms lowercase, uppercase, number, symbol and length rules work independently.

3. **Demo password**
   - **Test:** Meets every rule for the demo password.
   - **Sign:** The password is `Securepass123!`.
   - **Proof:** Confirms the demo password passes every rule.

4. **Valid password**
   - **Test:** Accepts a valid password.
   - **Sign:** The password meets all requirements.
   - **Proof:** Confirms no problem is reported for a good password.

5. **Password rejection (5 cases)**
   - **Test:** Explains why each invalid password is rejected.
   - **Sign:** A password is too short or lacks lowercase, uppercase, a number or a symbol.
   - **Proof:** Confirms each failure has its own explanatory message.

6. **Unsupported special characters**
   - **Test:** Rejects special characters outside the allowed set.
   - **Sign:** The password uses `&` as its symbol.
   - **Proof:** Confirms `&` does not count; only `! @ # % $` are allowed.

7. **Maximum password length**
   - **Test:** Rejects passwords longer than 128 characters.
   - **Sign:** The password exceeds 128 characters.
   - **Proof:** Confirms the upper limit matches the backend.

#### `src/utils/format.test.ts` (7 tests): text for people

1. **Minute formatting (4 cases)**
   - **Test:** Formats minute values into readable durations.
   - **Sign:** The input is 0, 45, 60 or 125 minutes.
   - **Proof:** Displays `0 min`, `45 min`, `1 h 0 min` and `2 h 5 min`.

2. **Known code labels**
   - **Test:** Returns the friendly label for a known code.
   - **Sign:** The code is `loading`.
   - **Proof:** Displays `Loading`.

3. **Retired or unknown codes**
   - **Test:** Falls back to the raw code when retired or unknown.
   - **Sign:** A code has no available friendly label.
   - **Proof:** Confirms old records still display something sensible.

4. **UTC timestamp formatting**
   - **Test:** Treats the server timestamp as UTC and shows it in local time.
   - **Sign:** A stored timestamp represents a UTC time.
   - **Proof:** Confirms the time appears in the viewer's time zone.

#### `src/utils/dates.test.ts` (3 tests): filter dates

1. **No date selected**
   - **Test:** Returns `undefined` when no day is chosen.
   - **Sign:** The date field is empty.
   - **Proof:** Confirms an empty date box adds no filter.

2. **Naive timestamp format**
   - **Test:** Returns naive timestamps without `Z` or an offset.
   - **Sign:** A timestamp is prepared for the API.
   - **Proof:** Confirms the format matches what the API expects.

3. **Full local-day range**
   - **Test:** Sets the start to local midnight and the end to the last second of the same local day.
   - **Sign:** The user selects a date for filtering.
   - **Proof:** Confirms the picked day covers the entire day in the user's time zone.

#### `src/api/client.test.ts` (14 tests): talking to the API

1. **Bearer token**
   - **Test:** Sends the saved token as a Bearer header.
   - **Sign:** The user is signed in.
   - **Proof:** Confirms authenticated calls carry the token.

2. **Authorization header**
   - **Test:** Sends no Authorization header when there is no token or authentication is off.
   - **Sign:** A login request is being made or no token exists.
   - **Proof:** Confirms login calls never send a token.

3. **JSON request formatting**
   - **Test:** Serializes a body as JSON and sets the content type only when a body exists.
   - **Sign:** A request includes or omits a body.
   - **Proof:** Confirms requests are well formed.

4. **Response parsing**
   - **Test:** Returns parsed JSON and `undefined` for a `204` response.
   - **Sign:** The server returns normal JSON or no content.
   - **Proof:** Confirms both response types work.

5. **API errors**
   - **Test:** Throws an `ApiError` carrying the server message and status.
   - **Sign:** The server returns an error response.
   - **Proof:** Confirms screens can show the server's explanation.

6. **Validation error lists**
   - **Test:** Joins the messages of a validation error list.
   - **Sign:** The server returns multiple validation errors.
   - **Proof:** Confirms errors become one readable line.

7. **Non-JSON error response**
   - **Test:** Falls back to a generic message when the body is not JSON.
   - **Sign:** The server returns an unreadable or non-JSON error body.
   - **Proof:** Confirms failures are handled cleanly.

8. **Authenticated `401`**
   - **Test:** Clears the token and calls the handler for an authenticated `401`.
   - **Sign:** An authenticated request returns `401`.
   - **Proof:** Confirms expired sessions sign the user out.

9. **Login `401`**
   - **Test:** Does not sign anyone out when a login attempt returns `401`.
   - **Sign:** Login fails because the credentials are incorrect.
   - **Proof:** Confirms the user stays on the login page.

10. **Password-change `400`**
    - **Test:** Keeps the user signed in for a `400`, such as a wrong current password.
    - **Sign:** The password-change request is rejected.
    - **Proof:** Confirms a password typo does not log the user out.

11. **CSV download success**
    - **Test:** Sends the auth header, saves the response as a file, then releases the URL.
    - **Sign:** An authenticated CSV download is requested.
    - **Proof:** Confirms the download works and cleans up afterward.

12. **CSV download failure**
    - **Test:** Throws an `ApiError` when the download is refused.
    - **Sign:** The server rejects the download request.
    - **Proof:** Confirms a refused download is reported.

13. **UTC timestamp formatting**
    - **Test:** `nowUtcIso` returns a naive UTC timestamp without a `Z`.
    - **Sign:** The application generates a timestamp for the backend.
    - **Proof:** Confirms sent times match the backend's format.

14. **Server date parsing**
    - **Test:** `parseServerDate` reads naive dates as UTC and respects an explicit offset.
    - **Sign:** A stored date has no timezone or includes an offset.
    - **Proof:** Confirms stored times convert correctly.

#### `src/api/manager.test.ts` (5 tests): manager calls

1. **No filters**
   - **Test:** Returns an empty string when there are no filters.
   - **Sign:** No filter values are supplied.
   - **Proof:** Confirms there is no stray `?` in the URL.

2. **Filters with values**
   - **Test:** Keeps only filters that have a value, including numbers.
   - **Sign:** Some filters are empty while others contain values.
   - **Proof:** Confirms empty filters are dropped.

3. **Safe URL encoding**
   - **Test:** Encodes values safely.
   - **Sign:** Filter values contain characters that need escaping.
   - **Proof:** Confirms times in the URL are escaped correctly.

4. **CSV report path**
   - **Test:** `reportCsvPath` points to the CSV route with the same filters.
   - **Sign:** A CSV report is requested with active filters.
   - **Proof:** Confirms the download uses the same filters as the screen.

5. **Performance trends request**
   - **Test:** `fetchPerformanceTrends` sends `group_by` and the date range.
   - **Sign:** The application requests performance trends.
   - **Proof:** Confirms the call uses the correct path and options.

#### `src/theme/useTheme.test.tsx` (6 tests): themes

1. **Valid themes**
   - **Test:** Accepts the four themes and rejects anything else.
   - **Sign:** A theme value is selected or loaded.
   - **Proof:** Confirms only Soft, Light, Grey and Dark are valid.

2. **Default theme**
   - **Test:** Starts on the default theme and applies it to the page.
   - **Sign:** A new user has no saved theme.
   - **Proof:** Confirms the page starts with the Soft colour theme.

3. **Theme selection**
   - **Test:** Applies a new theme and saves it for that user.
   - **Sign:** The user selects a different theme.
   - **Proof:** Confirms the choice is displayed and remembered.

4. **Separate user preferences**
   - **Test:** Keeps each user's choice separate.
   - **Sign:** Two people use the same computer.
   - **Proof:** Confirms each person retains their own theme.

5. **Invalid saved theme**
   - **Test:** Ignores an invalid saved value.
   - **Sign:** The stored theme value is invalid or corrupted.
   - **Proof:** Confirms the application safely falls back to the default.

6. **Theme reset on sign-out**
   - **Test:** Removes the theme from the page when the signed-in frame goes away.
   - **Sign:** The user signs out and the authenticated frame is removed.
   - **Proof:** Confirms signing out restores the default appearance.
#### `src/components/PasswordInput.test.tsx` (4 tests)

1. **Password hidden by default**
   - **Test:** Hides the typed text by default.
   - **Sign:** The user enters a password.
   - **Proof:** Confirms passwords appear as dots.

2. **Password typing**
   - **Test:** Accepts typing.
   - **Sign:** The user enters text into the field.
   - **Proof:** Confirms the field works normally.

3. **Password visibility toggle**
   - **Test:** Shows the text when the eye is clicked and hides it again.
   - **Sign:** The user clicks the eye icon.
   - **Proof:** Confirms the eye toggles password visibility.

4. **Eye button does not submit**
   - **Test:** Does not submit the form when the eye is clicked.
   - **Sign:** The user clicks the visibility toggle.
   - **Proof:** Confirms checking a password never submits the form.

#### `src/components/admin/PasswordRules.test.tsx` (4 tests)

1. **Empty password**
   - **Test:** Shows all five rules as unmet (red) for an empty password.
   - **Sign:** The password field is empty.
   - **Proof:** Confirms the checklist starts red.

2. **Live rule feedback**
   - **Test:** Turns the rules that are met green while the rest stay red.
   - **Sign:** The user types a password that meets some requirements.
   - **Proof:** Confirms feedback updates as the user types.

3. **Valid password**
   - **Test:** Shows every rule as met for a valid password.
   - **Sign:** The password meets all five rules.
   - **Proof:** Confirms a good password is all green.

4. **Blank password when editing**
   - **Test:** Shows a "keep current password" hint when editing a blank password.
   - **Sign:** A user is being edited without changing their password.
   - **Proof:** Confirms editing a user does not require a new password.

#### `src/components/SimpleTable.test.tsx` (3 tests)

1. **Table rows and headers**
   - **Test:** Renders a header row and one row per item.
   - **Sign:** Column definitions and data are provided.
   - **Proof:** Confirms tables are built from column definitions.

2. **Empty table**
   - **Test:** Shows the default message and no table when there are no rows.
   - **Sign:** The data contains no rows.
   - **Proof:** Confirms empty results are explained.

3. **Custom empty message**
   - **Test:** Shows a custom empty message when one is given.
   - **Sign:** A screen supplies its own empty-state message.
   - **Proof:** Confirms screens can explain what "empty" means.

#### `src/components/operator/SummaryCards.test.tsx` (10 tests)

1. **Card titles, values and labels**
   - **Test:** Shows the title and every value with its label.
   - **Sign:** Summary data is provided to the cards.
   - **Proof:** Confirms cards display their numbers and labels.

2. **Metric-specific colours (8 cases)**
   - **Test:** Applies the expected colour to each metric card.
   - **Sign:** A card displays a delay, container, productivity, task, shift or count metric.
   - **Proof:** Delay figures are amber; containers and productivity are green; tasks and shifts are blue; counts are slate.

3. **Explicit colour override**
   - **Test:** Uses an explicit tone instead of the inferred one.
   - **Sign:** A screen supplies a specific tone for a card.
   - **Proof:** Confirms a screen can override the inferred colour.

#### `src/components/admin/ReferenceDataForm.test.tsx` (8 tests)

1. **Locked existing code**
   - **Test:** Read-only and labelled as locked, with no notice until touched.
   - **Sign:** An existing code is selected for editing.
   - **Proof:** Confirms an existing code cannot be edited.

2. **Locked-code notice**
   - **Test:** Shows the red notice when clicked and hides it when focus leaves.
   - **Sign:** The user interacts with the locked code field.
   - **Proof:** Confirms the explanation appears only after interaction.

3. **Typing in locked code**
   - **Test:** Shows the notice when someone types, while the code stays unchanged.
   - **Sign:** The user attempts to modify the locked code.
   - **Proof:** Confirms typing is blocked and explained.

4. **Editable new code**
   - **Test:** Has an editable code and never shows the locked notice when adding.
   - **Sign:** The user creates a new reference value.
   - **Proof:** Confirms new values can choose a code.

5. **Code normalization**
   - **Test:** Normalizes the code and saves it in the chosen category.
   - **Sign:** The user enters `Quay Side`.
   - **Proof:** Confirms it is saved as `quay_side`.

6. **Invalid code**
   - **Test:** Rejects a code with invalid characters without calling the API.
   - **Sign:** The entered code contains unsupported characters.
   - **Proof:** Confirms invalid codes are stopped early.

7. **Untouched form**
   - **Test:** Says nothing has changed when saved untouched.
   - **Sign:** The user saves without editing any fields.
   - **Proof:** Confirms no empty updates are sent.

8. **Minimal update**
   - **Test:** Sends only the field that changed.
   - **Sign:** The user edits one field.
   - **Proof:** Confirms the update contains only the changed field.

#### `src/components/operator/ShiftPanel.test.tsx` (5 tests)

1. **Open shift details**
   - **Test:** Shows the MHC and shift code.
   - **Sign:** An operator has an open shift.
   - **Proof:** Confirms the open shift is displayed.

2. **Ending with an open task**
   - **Test:** Blocks ending the shift while a task is open and explains why in red.
   - **Sign:** The operator tries to end a shift with an active task.
   - **Proof:** Confirms the Phase 4 rule is enforced on screen.

3. **Cancelled confirmation**
   - **Test:** Does nothing when confirmation is cancelled.
   - **Sign:** The operator selects "Cancel".
   - **Proof:** Confirms the shift does not end.

4. **Confirmed shift end**
   - **Test:** Ends the shift with a naive UTC time once confirmed, then refreshes.
   - **Sign:** The operator confirms the end-shift action.
   - **Proof:** Confirms the correct data is sent.

5. **Shift-end failure**
   - **Test:** Shows the server message when ending fails.
   - **Sign:** The server rejects the request.
   - **Proof:** Confirms errors are visible.

#### `src/components/operator/TaskPanel.test.tsx` (7 tests)

1. **Starting a task**
   - **Test:** Offers lookup values and sends the choices with a naive UTC start time.
   - **Sign:** The operator selects a work type and working area.
   - **Proof:** Confirms the task starts with the chosen values.

2. **Optional fields**
   - **Test:** Omits optional fields that were left blank.
   - **Sign:** Vessel or bay fields are empty.
   - **Proof:** Confirms empty vessel or bay values are not sent.

3. **Required choices**
   - **Test:** Does not start a task until a work type and area are chosen.
   - **Sign:** One or both required choices are missing.
   - **Proof:** Confirms required choices are enforced.

4. **Friendly task labels**
   - **Test:** Shows friendly labels for the open task instead of raw codes.
   - **Sign:** The task has a stored work-type code.
   - **Proof:** Displays `Discharging`, not `discharging`.

5. **Ending with an open delay**
   - **Test:** Blocks ending while a delay is open and explains why in red.
   - **Sign:** The operator tries to end a task with an active delay.
   - **Proof:** Confirms a task cannot end during a delay.

6. **Required container count**
   - **Test:** Starts the container count empty and will not end without a number.
   - **Sign:** The operator leaves the count blank.
   - **Proof:** Confirms zero is not silently assumed.

7. **Deliberate zero count**
   - **Test:** Ends the task with the typed count, including a deliberate zero.
   - **Sign:** The operator explicitly enters `0`.
   - **Proof:** Confirms zero is accepted when entered intentionally.

#### `src/components/ChangePasswordDialog.test.tsx` (8 tests)

1. **Password rule checklist**
   - **Test:** Shows the rule checklist while the new password is typed.
   - **Sign:** Password requirements update as the user types.
   - **Proof:** Confirms live feedback for password rules.

2. **Password confirmation feedback**
   - **Test:** Warns when confirmation differs and clears the warning when it matches.
   - **Sign:** The two password entries do not match.
   - **Proof:** Confirms typos are caught immediately.

3. **Weak new password**
   - **Test:** Rejects a weak new password without calling the API.
   - **Sign:** The new password fails local validation.
   - **Proof:** Confirms local rules run before the API request.

4. **Mismatched confirmation**
   - **Test:** Rejects a confirmation that does not match.
   - **Sign:** The new password and confirmation differ.
   - **Proof:** Confirms both entries must agree.

5. **Reusing the current password**
   - **Test:** Rejects a new password equal to the current one.
   - **Sign:** The user enters the same password in both fields.
   - **Proof:** Confirms a password change must use a different password.

6. **Successful password change**
   - **Test:** Sends both passwords, then shows success and a Close button.
   - **Sign:** The API accepts the password-change request.
   - **Proof:** Confirms the correct request is sent and success is displayed.

7. **Incorrect current password**
   - **Test:** Shows the server message when the current password is wrong.
   - **Sign:** The API rejects the current password.
   - **Proof:** Confirms the user receives an explanation.

8. **Dialog dismissal**
   - **Test:** Closes on Escape and backdrop clicks, but not when the panel is clicked.
   - **Sign:** The user presses Escape, clicks outside the panel, or clicks inside it.
   - **Proof:** Confirms the dialog dismisses correctly without closing on an internal click.

#### `src/auth/RequireRole.test.tsx` (6 tests)

1. **Manager and admin access**
   - **Test:** Lets a manager and an admin open the guarded page (2 cases).
   - **Sign:** The user's role is permitted.
   - **Proof:** Confirms allowed roles can access the page.

2. **Wrong role**
   - **Test:** Sends an operator back to the operator home.
   - **Sign:** The operator attempts to access a manager-only page.
   - **Proof:** Confirms users with the wrong role cannot access manager pages.

3. **Signed-out visitor**
   - **Test:** Sends a signed-out visitor to the login page.
   - **Sign:** No authenticated session exists.
   - **Proof:** Confirms guarded pages require sign-in.

4. **Session check in progress**
   - **Test:** Waits while the saved session is being checked.
   - **Sign:** The application is still verifying the session after reload.
   - **Proof:** Prevents the login page from flashing before the check finishes.

5. **Role-based home pages**
   - **Test:** Maps every role to its own home page.
   - **Sign:** The user signs in with an operator, manager, or admin role.
   - **Proof:** Confirms each role lands on the correct home page.

#### `src/pages/LoginPage.test.tsx` (6 tests)

1. **Email and password fields**
   - **Test:** Shows an email field and a hidden password field.
   - **Sign:** Both fields appear correctly, and the password is masked.
   - **Fix/Proof:** Confirms the login form is complete.

2. **Login credentials submitted**
   - **Test:** Calls login with the typed email and password.
   - **Sign:** The submitted values match what the user entered.
   - **Fix/Proof:** Confirms the correct credentials are submitted.

3. **Invalid credentials**
   - **Test:** Shows the server message for a wrong email or password.
   - **Sign:** The API rejects the login attempt.
   - **Fix/Proof:** Confirms the user receives an explanation of the failed login.

4. **API unavailable**
   - **Test:** Shows a helpful message when the API cannot be reached.
   - **Sign:** The backend is stopped or unreachable.
   - **Fix/Proof:** Confirms the user receives a helpful error message.

5. **Login progress**
   - **Test:** Disables the button and shows progress while signing in.
   - **Sign:** A login request is in progress.
   - **Fix/Proof:** Prevents duplicate submissions and indicates progress.

6. **Already signed in**
   - **Test:** Skips the form and goes to the role home when already signed in.
   - **Sign:** The user has an active signed-in session.
   - **Fix/Proof:** Confirms signed-in users are redirected without seeing the login form.

## 10. How this project was created (reference)

You do not need these to run the project; they show how it was built. Run from `apps/mecandjeo-mhc-monitoring`.

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install react-router-dom
npm install -D vitest jsdom @testing-library/react \
  @testing-library/user-event @testing-library/jest-dom
npm pkg set scripts.test="vitest run" "scripts.test:watch=vitest"
```

The per-folder scripts and `scripts/test-here.mjs` were added afterwards (see `package.json`).

## 11. Troubleshooting

1. **Node.js missing or outdated**
   - **Symptom:** `node: command not found` or Node is older than 20.19.
   - **Sign:** Node.js is missing or too old.
   - **Fix:** Install the LTS version from [nodejs.org](https://nodejs.org), then reopen Git Bash.

2. **`npm install` fails or hangs**
   - **Symptom:** Installation fails or stops responding.
   - **Sign:** No internet connection or a blocking proxy.
   - **Fix:** Check your connection and run `npm install` again.

3. **Vite port 5173 is in use**
   - **Symptom:** `npm run dev` reports that port 5173 is occupied.
   - **Sign:** Another application is using the port.
   - **Fix:** Vite selects the next available port; open the address printed in the terminal.

4. **Login cannot reach the server**
   - **Symptom:** Login displays "Could not reach the server".
   - **Sign:** The backend may not be running.
   - **Fix:** Check with `docker compose --env-file .env.docker ps`, then start it using `docker compose --env-file .env.docker up -d`.

5. **HTTP proxy error or `ECONNREFUSED`**
   - **Symptom:** The terminal displays `http proxy error` or `ECONNREFUSED`.
   - **Sign:** The backend is stopped or unreachable.
   - **Fix:** Start the backend as described in Step 4.

6. **Demo account login fails**
   - **Symptom:** "Invalid email or password".
   - **Sign:** Demo data is missing or the credentials are incorrect.
   - **Fix:** Run `bash scripts/seed_demo_data.sh`. The demo password is `Securepass123!`.

7. **Unexpected return to the login page**
   - **Symptom:** The application sends you back to login after some time.
   - **Sign:** The authentication token has expired (24 hours).
   - **Fix:** Sign in again.

8. **Blank white page**
   - **Symptom:** The application displays a blank page.
   - **Sign:** A frontend error may have occurred.
   - **Fix:** Press F12 and inspect the browser Console; run `npm run build` to identify build errors.

9. **Old colors or layout after an update**
   - **Symptom:** The browser still displays the previous design.
   - **Sign:** The browser has cached old files.
   - **Fix:** Hard-refresh using **Ctrl+Shift+R**.

10. **Build error about an unused import**
    - **Symptom:** `npm run build` reports an unused import.
    - **Sign:** An imported item is no longer used.
    - **Fix:** Delete the unused import line.

11. **Missing `@testing-library/dom`**
    - **Symptom:** Tests report `Cannot find module '@testing-library/dom'`.
    - **Sign:** A required testing package is missing.
    - **Fix:** Run `npm install -D @testing-library/dom`.

12. **No test files found**
    - **Symptom:** `npm run test:here` prints `No test files found`.
    - **Sign:** You are in a folder without matching test files.
    - **Fix:** Change to a folder containing `.test` files using `cd`.

13. **Tests run slowly**
    - **Symptom:** `npm run test` takes longer than expected.
    - **Sign:** Each file starts a simulated browser.
    - **Fix:** Allow approximately 30 seconds; use a folder-specific command to run fewer tests.

14. **Unexpected redirect from `/api/cranes`**
    - **Symptom:** An address ending in `/api/cranes` redirects unexpectedly.
    - **Sign:** The trailing slash is missing.
    - **Fix:** Use `/api/cranes/`.



## 12. Phase 10 verification checklist

Run from the `frontend` folder with the backend running. Every line must pass.

- [ ] `npm install` finishes without errors
- [ ] `npm run build` finishes (TypeScript and Vite)
- [ ] `npm run lint` prints `Found 0 warnings and 0 errors`
- [ ] `npm run test` prints `16 passed` files and `107 passed` tests
- [ ] `npm run dev` shows `Local: http://localhost:5173/`
- [ ] `curl http://localhost:5173/health` prints `{"status":"ok"}`
- [ ] A wrong password shows a red "Invalid email or password"
- [ ] Operator, manager and admin accounts each land on their own screen
- [ ] An operator can start a shift, a task and a delay, and end them in order
- [ ] A manager sees the live overview and can download a CSV report
- [ ] An admin can add a user, a crane and a reference value
- [ ] Change password works from the header, and the old password stops working
- [ ] The theme choice survives a page refresh