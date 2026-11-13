<!-- DEPENDENCY-LOCKING.md: explains lock files (requirements.lock, package-lock.json), why they matter, how to update packages safely from now on, and how the app is put under version control. -->

# Dependency Locking and Updates Guide

This guide explains how the project makes builds repeatable, how you update packages on purpose, and how the application is kept under version control. It assumes no earlier experience.

Run commands from `apps/mecandjeo-mhc-monitoring` in **Git Bash** unless stated otherwise.

## Contents

1. The problem: "it worked yesterday"
2. The files
3. `requirements.txt` and `requirements.lock`: how they relate
4. Why a lock is needed even if every version is pinned
5. How `update_lock.sh` works
6. Creating or refreshing the lock
7. Proving the image matches the lock
8. How you will update packages from now on
9. Rolling back
10. Base images and operating-system packages
11. The npm side (frontend and e2e)
12. Version control (Git) for this app
13. Troubleshooting
14. Questions and answers

---

## 1. The problem: "it worked yesterday"

`requirements.txt` says `fastapi`, not *which* `fastapi`. Every time the image is rebuilt, pip installs the newest versions available that day, so two builds a few days apart can contain different packages. During this project that really happened: an image built days earlier held `fastapi 0.162.0` and `click 8.5.0`, while a fresh install gave `0.162.2` and `8.5.1`.

A **lock file** records the exact version of every package, and the build installs exactly those. The result:

| Benefit    | Meaning                                                                            |
|------------|------------------------------------------------------------------------------------|
| Repeatable | The image you tested is the image you deploy                                       |
| Reviewable | An update becomes a visible change: `git diff requirements.lock`                   |
| Reversible | Restore the old lock and rebuild to get the old behavior back                      |
| Auditable  | You can say exactly which version shipped, which a security finding often requires |

---

## 2. The files

1. **`requirements.txt`**
   - **Contains:** The packages you **choose** (11 lines).
   - **Who writes it:** You.
   - **Used by:** `update_lock.sh`.

2. **`requirements.lock`**
   - **Contains:** Every installed package with an exact version (about 25 lines).
   - **Who writes it:** `scripts/update_lock.sh`; never by hand.
   - **Used by:** The Docker build (`Dockerfile`) and `requirements-dev.txt`.

3. **`requirements-dev.txt`**
   - **Contains:** `-r requirements.lock`, plus `httpx` and `pytest`.
   - **Who writes it:** You.
   - **Used by:** Your local test environment.

4. **`frontend/package.json` and `frontend/package-lock.json`**
   - **Contains:** The frontend's chosen packages, and their exact versions.
   - **Who writes it:** `npm install`.
   - **Used by:** `npm ci` in `frontend/Dockerfile`.

5. **`e2e/package.json` and `e2e/package-lock.json`**
   - **Contains:** The browser tests' packages, and their exact versions.
   - **Who writes it:** `npm install`.
   - **Used by:** `npm ci` (later, in the pipeline).

**Important:** Commit lock files together with the code. A lock that is not committed protects nobody.

---

## 3. `requirements.txt` and `requirements.lock`: how they relate

**Direction.** The flow goes one way:

```text
requirements.txt  ──(scripts/update_lock.sh)──►  requirements.lock
 what you choose                                  what you get
```

Think of a **shopping list and a receipt**: the list says "11 things I want", the receipt records "the exact 25 items that went into the bag". The lock is never edited by hand, and you never copy its versions into `requirements.txt`. The one exception is a line you pin on purpose, with a reason, such as `bcrypt==4.0.1`.

**The lock does not update itself.**

It changes only when you run:

```bash
bash scripts/update_lock.sh
```

Later, a pipeline job can run it on a schedule.

**Why 11 became 25**

Your packages need other packages, and those need others in turn:

1. **`fastapi`**
   - Needs: `annotated-doc`, `opentelemetry-api`, `pydantic`, `starlette`, `typing-extensions`, `typing-inspection`.

2. **`uvicorn`**
   - Needs: `click`, `h11`, `typing-extensions`.

3. **`pydantic`**
   - Needs: `annotated-types`, `pydantic-core`, `typing-extensions`, `typing-inspection`.

4. **`email-validator`**
   - Needs: `dnspython`, `idna`.

5. **`alembic`**
   - Needs: `mako`, `sqlalchemy`, `typing-extensions`.

6. **`SQLAlchemy` and `PyJWT`**
   - Need: `typing-extensions`.

7. **`psycopg2-binary`, `python-dotenv`, `passlib` and `bcrypt`**
   - Need: Nothing else.

**Understanding the package count**

- **12 extra packages** are needed directly by your chosen packages.
- Two more are needed by those extras:
  - `anyio` by `starlette`.
  - `MarkupSafe` by `mako`.
- **14 extra packages in total.**

Therefore:

\[
11 + 14 = 25 \text{ packages}
\]
To see these relations for any package in your running image:

```bash
docker compose --env-file .env.docker run --rm --no-deps -T crane-app pip --disable-pip-version-check show fastapi
```

The lines `Requires:` and `Required-by:` list what it needs and who needs it.

---

## 4. Why a lock is needed even if every version is pinned

Suppose `requirements.txt` pinned all 11 packages (`fastapi==0.162.2` and so on). A lock would still matter, because those packages declare what **they** need as **ranges**. FastAPI, for example, says:

```text
starlette>=0.46.0
pydantic>=2.9.0
typing-extensions>=4.8.0
```

"Starlette 0.46.0 *or any newer version*." Pinning `fastapi` does not stop `starlette` from changing on the next rebuild. Pinning only the 11 packages you named leaves the other 14 free to float. The lock fixes the **whole tree**.

| Without a lock                                              | With a lock            |
|-------------------------------------------------------------|------------------------|
| 11 versions fixed by you, 14 unknown                        | All 25 fixed           |
| You must find and type every version                        | The script finds them  |
| A rebuild can silently change a library you never named     | A rebuild is identical |
| "Which version of X is in production?" needs detective work | Open the lock          |

A lock is not needed for a **library** that others install into their own projects, but this is an **application**, and applications should lock.

---

## 5. How `update_lock.sh` works

1. It checks that you are in the right folder and that Docker is running.
2. It starts a clean `python:3.12-slim` container (the same as the Dockerfile's base) and sends `requirements.txt` into it through standard input.
3. Inside, it runs `pip install` and then `pip freeze`, which prints every installed package as `name==version`.
4. The output is written to a **temporary file** (`requirements.lock.new`) with a two-line header.
5. It checks that the main packages (`fastapi`, `uvicorn`, `SQLAlchemy`, `alembic`) are in the result.
6. Only then does it replace `requirements.lock`.

If anything fails in steps 3 or 5, the old lock is left untouched and no temporary file remains. The lock is generated **inside a Linux container** on purpose: it must describe what the Linux image will install, not what your Windows machine would.

---

## 6. Creating or refreshing the lock

```bash
bash scripts/update_lock.sh
```

Expected:

```text
Installing the packages from requirements.txt into a clean python:3.12-slim container ...
Wrote requirements.lock with 25 pinned packages.
```

Look at it:

```bash
head -n 8 requirements.lock
grep -c "==" requirements.lock
grep -E "^(bcrypt|fastapi|SQLAlchemy)==" requirements.lock
```

A lock looks like this (versions will be newer in yours):

```text
# Exact versions of every package in the container image. Generated by scripts/update_lock.sh: do not edit by hand.
# To change a package, edit requirements.txt and run: bash scripts/update_lock.sh
alembic==1.20.1
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.16.0
bcrypt==4.0.1
click==8.5.0
dnspython==2.9.2
email-validator==2.3.0
fastapi==0.162.0
h11==0.16.0
```

---

## 7. Proving the image matches the lock

After a rebuild, the image must contain exactly what the lock says:

```bash
docker compose --env-file .env.docker build --no-cache crane-app
docker compose --env-file .env.docker run --rm --no-deps -T crane-app \
  pip --disable-pip-version-check freeze 2>/dev/null \
  | tr -d '\r' | grep -E '^[A-Za-z0-9_.-]+==' \
  | diff - <(grep -E '^[A-Za-z0-9_.-]+==' requirements.lock) \
  && echo "the image matches the lock"
```

Expected: `the image matches the lock`. `bash scripts/verify_stack.sh` runs this same comparison as its "Reproducibility" check.

**What the filters are for.** `tr -d '\r'` removes Windows line endings, `grep` keeps only real `name==version` lines (so noise such as `failed to get console mode for stdout` cannot leak in), and `2>/dev/null` hides pip's harmless cache warning.

**The check can fail usefully.** In this project it once reported `click` and `fastapi` differing. The cause was an *older image* from before the lock existed: the rebuild had not completed. A check that can fail is what makes a passing check trustworthy.

---

## 8. How you will update packages from now on

### 8.1 The routine

```text
1. Edit requirements.txt (or leave it as is, to pick up newer versions)
2. bash scripts/update_lock.sh                          creates a new lock
3. git diff requirements.lock                           shows exactly which packages changed
4. docker compose --env-file .env.docker build --no-cache crane-app
5. Test and check:
     python -m pytest tests -q
     docker compose --env-file .env.docker up -d --wait
     bash scripts/verify_stack.sh
     bash scripts/scan_security.sh --strict
6. Commit requirements.lock (and requirements.txt if you changed it) with a message
```

Step 3 is the payoff: a package update is a small, readable change you can accept or reject.

### 8.2 Situations and commands

1. **Routine refresh (for example, monthly)**
   - Follow the routine above, without editing `requirements.txt`.

2. **Add a package**
   - Add its name on a new line in `requirements.txt`, then follow the routine.

3. **Remove a package**
   - Delete its line from `requirements.txt`, then follow the routine. The lock shrinks.

4. **A new version breaks something**
   - Put a limit in `requirements.txt` with a comment, for example:
     ```text
     starlette<1.10  # 1.10 breaks X
     ```
   - Then follow the routine. Alternatively, restore the old lock (section 9).

5. **The scanner flags a Python package**
   - Run the routine: `update_lock.sh` fetches the fixed version listed in the report.
   - Check that the diff shows the update, then rebuild and rescan.

6. **The scanner flags an operating-system package**
   - No lock change is needed.
   - Run:
     ```bash
     docker compose --env-file .env.docker build --pull --no-cache crane-app
     ```
   - See `docs/PROJECT-PHASES/Phase-11.1-CONTAINER-SECURITY.md`.

7. **Update only one package**
   - `update_lock.sh` always refreshes everything to the newest allowed versions.
   - To hold the others back, put limits on them in `requirements.txt`; or accept the full refresh and review the diff.

### 8.3 Handy commands for beginners

1. **What would the build install?**
   ```bash
   cat requirements.lock
   ```

2. **How many packages are pinned?**
   ```bash
   grep -c "==" requirements.lock
   ```

3. **What exactly changed in the last refresh?**
   ```bash
   git diff requirements.lock
   ```

4. **What is inside the running image?**
   ```bash
   docker compose --env-file .env.docker run --rm --no-deps -T crane-app pip freeze
   ```

5. **Who needs this package?**
   ```bash
   docker compose --env-file .env.docker run --rm --no-deps -T crane-app pip --disable-pip-version-check show PACKAGE
   ```

6. **Is my test environment the same as the image?**
   ```bash
   pip install -r requirements-dev.txt
   ```
   Then run `pip freeze` and compare with the lock.

7. **Reinstall my test environment**
   ```bash
   pip install -r requirements-dev.txt
   ```

---

## 9. Rolling back

If a refresh causes trouble, return to the previous lock and rebuild:

```bash
git checkout -- requirements.lock          # undo an uncommitted change
# or, after committing, bring back the lock from an earlier commit:
git log --oneline -- requirements.lock     # find the commit
git checkout COMMIT_ID -- requirements.lock
docker compose --env-file .env.docker build --no-cache crane-app
docker compose --env-file .env.docker up -d --wait
bash scripts/verify_stack.sh
```

This is possible only because the lock is committed.

---

## 10. Base images and operating-system packages

1. **Python packages**
   - **Policy:** **Locked**.
   - **Why:** They change how the app behaves.

2. **npm packages**
   - **Policy:** **Locked** (`package-lock.json`, installed with `npm ci`).
   - **Why:** Same.

3. **Base images** (`python:3.12-slim`, `node:22-alpine`, `nginx-unprivileged:stable-alpine`, `postgres:17`)
   - **Policy:** Follow a **maintained version line**, refreshed by rebuilding with `--pull --no-cache` and checked by the scan.
   - **Why:** Freezing a base image forever recreates the "61 findings" problem.

4. **Operating-system packages**
   - **Policy:** **Updated at every build** (`apt-get upgrade`, `apk upgrade`).
   - **Why:** Security fixes should arrive promptly.

5. **Trivy**
   - **Policy:** `aquasec/trivy:latest`.
   - **Why:** A scanner should always be current.

**Base image updates in the future**

The industry answer for base images is to pin them by **digest** (an exact fingerprint) and let a bot propose updates (Dependabot or Renovate).

That needs the pipeline, so it belongs to Phase 14. Until then: rebuild with `--no-cache` regularly and scan.

**Package hashes**

Lock files can also record a checksum of every package (`--require-hashes`), which protects against a tampered download.

This project does not use them yet; it is a candidate hardening for the pipeline phase.

---

## 11. The npm side (frontend and e2e)

1. **`npm ci`**
   - **Use:** Install **exactly** what `package-lock.json` says.
   - Used by the Dockerfile and by pipelines.
   - Fails if the lock and `package.json` disagree.

2. **`npm install`**
   - **Use:** Install and, if needed, **update** the lock.
   - Use it on your PC when you add a package.

3. **`npm install PACKAGE`**
   - **Use:** Add a package to `package.json` and the lock.

4. **`npm outdated`**
   - **Use:** List packages that have newer versions.

5. **`npm audit`**
   - **Use:** List known flaws in your npm packages.

**Important:** Commit `frontend/package-lock.json` and `e2e/package-lock.json` whenever they change.
---

## 12. Version control (Git) for this app

### 12.1 What `git status` shows

`git status` lists changes that are **not yet committed**. Once something is committed, it disappears from the list.

| Marker (`--short`) | Meaning                                             |
|--------------------|-----------------------------------------------------|
|       `??`         | A new file or folder Git has never seen (untracked) |
|      ` M`          | A tracked file you changed                          |
|      ` D`          | A tracked file you deleted                          |
|       `A `         | A file you staged with `git add`                    |
|   (nothing)        | No uncommitted changes in the repository            |

Git shows a folder that is **entirely untracked as one line**, such as `./`. That is why a whole new application can appear as a single entry instead of a list of files. `git status` is **repository-wide**: it also lists changes in other projects of the same repository. To look at this folder only:

```bash
git status --short .
```

### 12.2 Local repository and GitHub

`git status` talks only to your **local** repository. The line `Your branch is up to date with 'origin/main'` means a GitHub remote named `origin` exists and your local `main` matches it. They are two separate things: committing records changes **locally**; pushing sends them to GitHub. In this project nothing is pushed without your explicit approval.

This repository (`vpc-aws-terraform-infra`) holds several projects (Terraform modules, `apps/mecandjeo-school`, this app), so **always add only the folder you mean.**

> Never use `git add -A` or `git commit -a` here. They would sweep in other projects, database backups and Terraform edits.

### 12.3 Adding the app for the first time

Run from `apps/mecandjeo-mhc-monitoring`.

**Step 1. Confirm the secrets are ignored.** `.env.docker` holds passwords:

```bash
git check-ignore -v .env.docker frontend/node_modules e2e/node_modules
```

Expected: three lines, each naming the `.gitignore` rule that hides the path. If `.env.docker` is missing from the output, stop and fix `.gitignore` first.

**Step 2. Preview what would be added**, without adding anything:

```bash
git add --dry-run . | wc -l
git add --dry-run . | grep -E "\.env|\.sql|\.db|venv|node_modules|/dist/|__pycache__|playwright-report|test-results"
```

Expected: a few hundred files at most (this app: 175), and the second command listing only `.env.docker.example`, `.env.example` and `e2e/cleanup-test-data.sql`. Open the two example files and confirm they hold only placeholders, never real passwords:

```bash
cat .env.example
cat .env.docker.example
```

**Step 3. Stage only this folder and review:**

```bash
git add .
git status --short . | head -20
git diff --cached --stat | tail -3
```

`git add .` adds only what is under the folder you are in.

**Step 4. Commit locally:**

```bash
git commit -m "feat(mhc-monitoring): add crane monitoring application through phase 11"
git log --oneline -2
git status
```

Expected: the new commit at the top of the log, and `git status` saying your branch is **ahead of 'origin/main' by 1 commit**: it exists locally and is not on GitHub.

### 12.4 Commit style

The repository uses *conventional commits*: `type(scope): message`. Examples for this app:

| Change                      | Message                                                 |
|-----------------------------|---------------------------------------------------------|
| Refresh the locked packages | `chore(mhc-monitoring): refresh locked Python packages` |
| A bug fix                   | `fix(mhc-monitoring): ...`                              |
| A new feature               | `feat(mhc-monitoring): ...`                             |
| Documentation               | `docs(mhc-monitoring): ...`                             |
| Tests                       | `test(mhc-monitoring): ...`                             |

After the first commit, make small commits for each change:

```bash
git add requirements.lock requirements.txt
git commit -m "chore(mhc-monitoring): refresh locked Python packages"
```

Before any push, ask for approval; then `git push` sends the commits to GitHub.

---

## 13. Troubleshooting

1. **`update_lock.sh`: "The install failed, so requirements.lock was NOT changed"**
   - **Cause:** A package name or version in `requirements.txt` does not exist, or there is no internet connection.
   - **Fix:** Read the pip error above that line and fix `requirements.txt`.

2. **The image-matches-lock check fails**
   - **Cause:** The image is older than the lock.
   - **Fix:** Run:
     ```bash
     docker compose --env-file .env.docker build --no-cache crane-app
     docker compose --env-file .env.docker up -d --wait
     ```

3. **`pip install -r requirements-dev.txt` fails on a package**
   - **Cause:** A locked version has no Windows build.
   - **Fix:** Report the package; the dev file can install it unpinned.

4. **A refreshed lock breaks the tests**
   - **Cause:** A newer package changed behavior.
   - **Fix:** Roll back (section 9), then limit that package in `requirements.txt`.

5. **`WARNING: The directory '/home/app/.cache/pip' ...`**
   - **Cause:** The `app` user has no home folder.
   - **Fix:** Harmless; add `--disable-pip-version-check`.

6. **`git status --short` prints nothing or one `./` line**
   - **Cause:** See section 12.1.
   - **Fix:** Check `git ls-files`, and whether the folder was ever committed.
---

## 14. Questions and answers

1. **Does `requirements.lock` update itself?**
   - No. Only `bash scripts/update_lock.sh` changes it.
   - A pipeline can run it on a schedule later.

2. **What is the relationship between the 11 packages and the 25?**
   - `requirements.txt` is what you choose.
   - The lock is what you get, including everything your packages need.
   - It is generated from `requirements.txt`.

3. **Should I copy the lock's versions into `requirements.txt`?**
   - No. Pin a line in `requirements.txt` only deliberately, with a reason (such as `bcrypt==4.0.1`).

4. **If `requirements.txt` pinned all 11 packages, would I still need a lock?**
   - Yes. Their own requirements are version ranges, so 14 other packages would still float (section 4).

5. **What was `requirements.lock.EXAMPLE`?**
   - An illustration shown during the lesson.
   - It is not part of the project and nothing reads it; delete it.
   - Your real lock is `requirements.lock`, created by `update_lock.sh`.

6. **Why is the lock generated in Docker rather than on my PC?**
   - It must describe what the Linux image will install (Linux, Python 3.12), not what Windows would.

7. **Why did the first lock check fail?**
   - The image was older than the lock (built before the lock existed).
   - The check caught it, and a rebuild fixed it.

8. **`git status` showed nothing for the app. Did I forget to create the GitHub repository?**
   - No. The remote `origin` already existed.
   - The app folder had never been added to Git, and Git displays an untracked folder as one `./` line (section 12.1).

9. **Why not `git add -A`?**
   - This repository contains several projects and unrelated edits; add only the folder you mean (section 12.2).

10. **Why is `package-lock.json` committed?**
    - So `npm ci` reproduces the same frontend, here and in the pipeline.

11. **Where does this go next?**
    - Phase 14 runs `npm ci`, installs from `requirements.lock`, and rebuilds and scans on a schedule, so updates arrive as reviewable changes instead of surprises.