<!-- CONTAINER-SECURITY.md: explains how the project's containers are hardened (non-root, health checks, operating-system fixes) and how to scan them with Trivy and respond to findings. -->

# Container Security Guide

This guide explains how the containers of this project are made safer, how to scan them for known security flaws, and how to respond when the scanner finds something. It assumes no earlier security experience. Every idea is shown with the file where it lives and a command you can run.

Run commands from `apps/mecandjeo-mhc-monitoring` in **Git Bash** unless stated otherwise.

## Contents

1. Why this matters
2. Non-root containers
3. Runtime packages and development packages
4. Health checks and timing
5. Operating-system fixes at build time
6. Trivy: the scanner
7. Running the scans
8. Reading a scan report
9. Responding to findings
10. Commands cheat sheet
11. Troubleshooting
12. Questions and answers

---

## 1. Why this matters

A container image is built from layers of other people's software: the operating system, Python or NGINX, and every library. New flaws in that software are published every day, and a program that runs as an all-powerful user makes every flaw worse.

Two habits reduce the risk:

1. **Least privilege**
   - **What it means:** Programs run as an ordinary user, never as `root`.
   - **Where it lives here:** `Dockerfile`, `frontend/Dockerfile`.

2. **Scan and fix, repeatedly**
   - **What it means:** Compare what is inside the images with a database of known flaws, and update.
   - **Where it lives here:** `scripts/scan_security.sh`, `.trivyignore`.

### Important security principle

Security is not a state you reach. A clean scan today only means "no known flaw today".

The skill is the continuous improvement loop:

**Detect → Understand → Fix at the right layer → Verify**

Section 9 walks through real examples from this project.

---

## 2. Non-root containers

By default, the program inside a container runs as `root`. If someone ever broke into the application, they would hold root powers inside the container. Running as an ordinary user limits the damage.

### 2.1 The backend image (`Dockerfile`)

```dockerfile
# Apply the operating system's available security fixes ...
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# A dedicated unprivileged user ...
RUN groupadd --system app && useradd --system --gid app --no-create-home --shell /usr/sbin/nologin app

COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock

COPY --chown=app:app app ./app
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app migrations ./migrations

USER app
```

### Understanding the non-root Dockerfile instructions

1. **`RUN groupadd --system app && useradd --system ...`**
   - **Meaning:** Creates a user and group named `app`.
   - `--system` marks it as a service account.
   - `--no-create-home` gives it no home folder.
   - `--shell /usr/sbin/nologin` means nobody can log in as it.

2. **`COPY --chown=app:app app ./app`**
   - **Meaning:** Copies the folder `app` from your computer into the image at `/app/app`.
   - Makes the files owned by user `app` and group `app`.
   - The format is `user:group`.

3. **`USER app`**
   - **Meaning:** From here on, and when the container runs, the program runs as user `app`.

**Why `--chown`?** Copied files belong to `root` by default. A program can read files owned by root but cannot write next to them (Python, for example, writes cache files). Making the application own its files gives it what it needs and nothing more.

**Why does the order matter?** Installing packages and applying updates need root, so they come **before** `USER app`.

**The rule "the last `USER` wins".** A Dockerfile can switch users several times, and the container finally runs as the one named last. Scanners check the last `USER` line of the last stage.

### 2.2 The web image (`frontend/Dockerfile`)

```dockerfile
FROM nginxinc/nginx-unprivileged:stable-alpine
USER root
RUN apk upgrade --no-cache
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
USER 101
EXPOSE 8080
```

The "unprivileged" nginx image already runs as user 101 and listens on port 8080 (ports below 1024 are reserved for root). The Dockerfile switches to root only for the update step and then **states `USER 101` explicitly**. It changes nothing at runtime, but it lets scanners and policies verify the safety by reading the file (the scanner flagged its absence as a HIGH finding, `DS-0002`).

### 2.3 Verify it

```bash
docker compose --env-file .env.docker exec crane-app id
docker compose --env-file .env.docker exec crane-web id
```

Expected:

```text
uid=999(app) gid=999(app) groups=999(app)
uid=101(nginx) gid=101(nginx) groups=101(nginx)
```

Neither says `uid=0(root)`. `bash scripts/verify_stack.sh` checks this automatically (the "Security" section).

---

## 3. Runtime packages and development packages

The production image should contain only what the application needs to run. Test tools stay out.

1. **`requirements.txt`**
   - **Contains:** The packages you choose (runtime only).
   - **Used by:** You edit it; `update_lock.sh` reads it.

2. **`requirements.lock`**
   - **Contains:** The exact version of every package that gets installed.
   - **Used by:** The Docker build.

3. **`requirements-dev.txt`**
   - **Contains:** The lock, plus `pytest` and `httpx`.
   - **Used by:** Your local test environment.

Inside `requirements-dev.txt`:

```text
-r requirements.lock
httpx
pytest
```

**`-r` means "read".** `pip install -r file` installs the packages listed in the file (without `-r`, pip would treat the file name as a package name). Inside a requirements file, a line `-r other-file` means "also read the packages listed in that other file". So the dev file equals the lock plus two test tools, without copying the list. The full story of the lock is in `docs/PROJECT-PHASES/Phase-11.2-DEPENDENCY-LOCKING.md`.

Check the image really has no test tools:

```bash
docker compose --env-file .env.docker run --rm --no-deps -T crane-app \
  pip --disable-pip-version-check freeze 2>/dev/null | grep -iE "^(pytest|httpx)==" || echo "no test packages in the image"
```

Expected: `no test packages in the image`.

---

## 4. Health checks and timing

A **health check** is a small question Docker asks a container on a schedule ("are you OK?"). `depends_on` and `--wait` rely on the answer.

| Service     | `interval` | `start_period` | `start_interval` |
|-------------|------------|----------------|------------------|
| `crane-db`  |    10 s    |     20 s       |     2 s          |
| `crane-app` |    30 s    |     20 s       |     2 s          |
| `crane-web` |    30 s    |     10 s       |     2 s          |

| Setting          | Meaning                                                    |
|------------------|------------------------------------------------------------|
| `interval`       | How often the check runs once the container is established |
| `start_period`   | A grace period after start: failures in it do not count    |
| `start_interval` | How often the check runs **during** `start_period`         |

**The lesson from this project.** Without `start_interval`, the first check runs one full `interval` after the container starts. After restarting `crane-web` (interval 30 seconds), a `sleep 20` was too short: it was still `starting`, and the stack check reported one failure. With `start_interval: 2s`, the container reported healthy about 5 seconds after starting.

**Use `--wait` instead of `sleep`:**

```bash
docker compose --env-file .env.docker up -d --wait
```

It returns only when every service is healthy, or fails if one does not become healthy. That is how pipelines should wait.

**Why did `up -d --force-recreate --wait crane-web` take more than a minute?** `--force-recreate crane-web` also recreates everything `crane-web` depends on (the API, the migration job and the database) and waits for each in turn. To touch only one container, add `--no-deps`:

```bash
docker compose --env-file .env.docker up -d --force-recreate --no-deps --wait crane-web
```

`start_interval` needs a recent Docker Engine (version 25 or newer). Validate the file with `docker compose --env-file .env.docker config -q`: no output means it is valid.

Docker health checks are used by Compose. Other platforms define their own: the ECS task definition (Phase 12) and Kubernetes probes (Phase 15). That is why the Dockerfiles carry no `HEALTHCHECK` line (section 7.3).

---

## 5. Operating-system fixes at build time

Linux distributions publish security fixes in their own repositories, often **before** the Docker base image is rebuilt. Applying pending fixes during the build closes that gap.

### Operating-system update commands

1. **Backend (`python:3.12-slim`, Debian)**
   - **Command in the Dockerfile:**
     ```dockerfile
     RUN apt-get update \
         && apt-get upgrade -y --no-install-recommends \
         && rm -rf /var/lib/apt/lists/*
     ```
   - **Package manager:** `apt`.

2. **Web (`nginx-unprivileged:stable-alpine`, Alpine)**
   - **Command in the Dockerfile:**
     ```dockerfile
     RUN apk upgrade --no-cache
     ```
   - **Package manager:** `apk`.
   - **Important:** Run this command as `USER root`, then switch back to `USER 101`.

Two things to remember:

1. **Build caching.** Docker reuses a layer when its command has not changed, so the update command would not fetch new fixes on later builds. Rebuild with `--no-cache` (and `--pull`, to fetch a fresh base image) regularly:

   ```bash
   docker compose --env-file .env.docker build --pull --no-cache
   docker compose --env-file .env.docker up -d --wait
   ```

### 2. The policy, in one table

1. **Python and npm packages**
   - **Policy:** Locked to exact versions.
   - **Why:** They change how the application behaves.

2. **Base images**
   - **Policy:** Follow a maintained version line, refreshed by rebuilding.
   - **Why:** Freezing an old tag forever produced 61 findings (see section 9).

3. **Operating-system packages**
   - **Policy:** Updated at every build.
   - **Why:** Security fixes should arrive promptly.

   The trade-off: operating-system packages are not frozen, so two builds a week apart can differ slightly. The scan is what keeps that safe. In Phase 14 a pipeline will rebuild and scan on a schedule.

---

## 6. Trivy: the scanner

**Trivy** is a free, widely used scanner from Aqua Security. It can check the following:

### What Trivy can scan

1. **Container images**
   - **What it finds:** Known flaws (CVEs) in operating-system packages and language packages (Python, Node).
   - **Used here:** Yes.

2. **Dockerfiles and infrastructure files (`config`)**
   - **What it finds:** Risky settings, for example, "no non-root user".
   - **Used here:** Yes. It also scanned your Terraform in `infra/` and reported 0 findings.

3. **Folders**
   - **What it finds:** Secrets such as keys and flaws in dependency files.
   - **Used here:** Not yet.

### What is a CVE?

**CVE** stands for *Common Vulnerabilities and Exposures*. It is a public identifier for a known security flaw, such as `CVE-2026-85091`.

Each CVE has a severity rating:

- **LOW**
- **MEDIUM**
- **HIGH**
- **CRITICAL**

### 6.1 Trivy in a container versus Trivy on your PC

You may have Trivy installed on your PC. `scripts/scan_security.sh` does **not** use it; it runs Trivy as a container.

|                  | The script                            | Trivy installed on your PC |
|------------------|---------------------------------------|----------------------------|
| The program      | Aqua Trivy                            | The same program           |
| How it runs      | `docker run aquasec/trivy:latest ...` | `trivy ...`                |
| Needs installing | No                                    | Yes                        |
| Version          | Always the newest image               | The one you installed      |
| Database cache   | The Docker volume `trivy-cache`       | A folder on your PC        |

The script uses the container so that nothing has to be installed and every machine (and the Phase 14 pipeline) uses the same version. Your installed copy stays useful for quick manual scans of any folder, for example `trivy config infra/` for Terraform, or `trivy image mecandjeo-mhc-monitoring:dev`. With equally fresh databases both give the same answers.

---

## 7. Running the scans

### 7.1 The command

```bash
bash scripts/scan_security.sh                  # shows findings, exit code 0
bash scripts/scan_security.sh --strict         # exit code 1 when serious findings exist
bash scripts/scan_security.sh config           # only the Dockerfiles
bash scripts/scan_security.sh images           # only the two images
SEVERITY=LOW,MEDIUM,HIGH,CRITICAL bash scripts/scan_security.sh config   # include minor findings
```

The first run downloads the Trivy container and the vulnerability database (a minute or two). The database is kept in the `trivy-cache` volume, so later runs are fast. Full option and exit-code tables: `docs/PROJECT-PHASES/Phase-11.5-SCRIPTS-REFERENCE.md`, section 4.

By default only **HIGH and CRITICAL** findings are reported, and for images only those **that already have a fix** (`--ignore-unfixed`), because you cannot act on a flaw nobody has fixed yet.

### 7.2 The Dockerfile scan

Checks the Dockerfiles for risky settings. Folders containing other people's code (`node_modules`, `dist`, and virtual environments) are skipped.

#### Findings in this project

1. **`DS-0002` — HIGH**
   - **Meaning:** "Specify at least 1 USER command with a non-root user".
   - **Outcome:** **Fixed.**
     - Added `USER 101` to `frontend/Dockerfile`.
     - An unused `Dockerfile.multistage` had the same finding and was **deleted**.

2. **`DS-0026` — LOW**
   - **Meaning:** "Add HEALTHCHECK instruction in your Dockerfile".
   - **Outcome:** **Accepted** with a written reason (see section 7.3).

### 7.3 Accepting a finding on purpose: `.trivyignore`

```text
# Findings we have looked at and deliberately accept. Each line is a check id; the comment says why.
# DS-0026: no HEALTHCHECK instruction inside the Dockerfile. Health checks are defined where the container is run
# (docker-compose.yml now; the ECS task definition and Kubernetes probes later), so the image does not carry its own.
DS-0026
```

The rule for this file: **a finding is fixed, or accepted with a written reason.** An exception without a reason hides a problem. For a vulnerability, add its CVE id on its own line with a comment saying why and when to review it. To see what the file hides, rename it temporarily:

```bash
mv .trivyignore .trivyignore.off
SEVERITY=LOW,MEDIUM,HIGH,CRITICAL bash scripts/scan_security.sh config
mv .trivyignore.off .trivyignore
```

(Restore it afterwards.)

### 7.4 The image scan

Scans the two built images (`mecandjeo-mhc-monitoring:dev` and `mecandjeo-mhc-web:dev`) through the Docker socket. They must exist locally; if not, the script says `not built` and tells you the build command.

---

## 8. Reading a scan report

A finding looks like this:

```text
mecandjeo-mhc-monitoring:dev (debian 13.7)
Total: 2 (HIGH: 2, CRITICAL: 0)

Library | Vulnerability  | Severity | Status | Installed Version | Fixed Version | Title
zlib1g  | CVE-2026-85091 | HIGH     | fixed  | 1:1.3...-1+b1     | 1:1.3...+deb13u1 | zlib: Heap buffer overflow ...
```

### Understanding the report

1. **Heading (`debian 13.7`)**
   - **Meaning:** The target is the **operating system** packages of the image.
   - A heading such as `Python` means libraries from your lock file.

2. **`Total`**
   - **Meaning:** Shows how many findings were detected, grouped by severity.

3. **Library**
   - **Meaning:** Identifies the package that contains the flaw.

4. **Vulnerability**
   - **Meaning:** The CVE ID. Search for it to read the security advisory.

5. **Status (`fixed`)**
   - **Meaning:** A repaired version exists. Findings without a fix are hidden by the script.

6. **Installed and Fixed Version**
   - **Meaning:** Shows the version currently in the image and the version that repairs the vulnerability.

### Dockerfile scan findings

A line in the Dockerfile report names the check ID (for example, `DS-0002`), its severity, and the affected file.
**A caution about titles.** The title comes from a public database and can occasionally be wrong or mismatched with the package. One finding in this project described a different product (a web-bundler plugin) while being reported against `zlib1g`. The package, installed version and fixed version are what you act on.

---

## 9. Responding to findings

### 9.1 The decision tree

1. **Finding under the operating system heading (`debian`, `alpine`), with a fixed version available**
   - **Meaning:** A system package needs updating.
   - **Fix:** Rebuild with:
     ```bash
     docker compose --env-file .env.docker build --pull --no-cache <service>
     ```
   - If it is still flagged, the update step in the Dockerfile (section 5) applies the fix. Confirm that the line exists.

2. **Finding under `Python` (or another language heading)**
   - **Meaning:** A package in `requirements.lock` is affected.
   - **Fix:** Run:
     ```bash
     bash scripts/update_lock.sh
     ```
     Fetch the fixed version, check `git diff requirements.lock`, rebuild with `--no-cache`, test and rescan.

3. **Very many findings in an image**
   - **Meaning:** The base image is old or unmaintained.
   - **Fix:** Move to a maintained tag, then rebuild.

4. **A fixed version is listed by the package manager (9.4), but the image still has the old version**
   - **Meaning:** The image was built before the fix was published.
   - **Fix:** Run `build --pull --no-cache <service>`, then rescan.

5. **No fixed version exists**
   - **Meaning:** Nothing to apply yet.
   - **Fix:** Hidden by the script. If a serious one matters to you, accept it in `.trivyignore` with a reason and a review date.

6. **Every finding of one kind in one file**
   - **Meaning:** A configuration problem.
   - **Fix:** Fix the file, or accept the check in `.trivyignore` with a reason.

**After any fix:** Rebuild, then run:

```bash
bash scripts/scan_security.sh --strict
bash scripts/verify_stack.sh
```

Then run the tests.

### 9.2 What happened in this project

1. **First scan — Web image**
   - **Observation:** 61 findings (58 HIGH, 3 CRITICAL) on Alpine 3.21.3.
   - **Decision:** The tag `nginx-unprivileged:1.27-alpine` was frozen on an old release. Moved to the maintained `stable-alpine`.

2. **After the move**
   - **Observation:** Web image had 6 findings (`brotli-libs`, `curl`, `libcurl`, `libexpat`). `stable-alpine` and `mainline-alpine` showed the same six.
   - **Decision:** The tag was not the problem: Alpine had published fixes after the image was built. Added `apk upgrade` to the Dockerfile.
   - **Result:** Clean.

3. **First scan — Backend**
   - **Observation:** 2 HIGH findings in `apt` and `libapt-pkg7.0` (fix 3.0.4).
   - **Decision:** A fresh `build --pull --no-cache` picked up a refreshed base image.
   - **Result:** Clean.

4. **Days later**
   - **Observation:** Backend had 2 HIGH findings in `zlib1g` (fix `...+deb13u1`), although it had been clean.
   - **Decision:** New flaws are published daily. Added `apt-get upgrade` to the Dockerfile.
   - **Result:** Clean.

5. **Dockerfile scan**
   - **Observation:** `DS-0002` HIGH in `frontend/Dockerfile` and `Dockerfile.multistage`.
   - **Decision:** Added `USER 101`; deleted the unused experimental file.

6. **Final check of the phase**
   - **Observation:** Web image had 2 HIGH findings in `libxslt` (fix `1.1.43-r4`), although it had been clean.
   - **Decision:** `apk policy libxslt` (section 9.4) showed `-r4` already in the repository: the image had been built **before** the fix was published. `build --pull --no-cache` picked it up.
   - **Result:** Clean.
   - **Additional finding:** It also showed `libxslt` is only there for an optional nginx XSLT module that this project does not use.

### 9.3 Lessons

- **"Clean" is a statement about today.** The backend image was clean and then was not, without anyone changing it.
- **A pinned tag ages.** Pinning is good for repeatability, but a pin that is never updated becomes the problem. Plan regular rebuilds and updates.
- **Fix at the right layer.** A base-image problem is fixed in the base image choice, an operating-system package by an update, a Python package in the lock.
- **Remove what you do not use.** An unused file still shows up in scans.
- Timing matters. A finding can appear before the repository has the fix, or a fix can appear after your last build. Check with the package manager (section 9.4) and rebuild with --no-cache.
- **The multi-stage build helps.** The Node build stage of the frontend is thrown away, so its flaws never reach the final image.


### 9.4 Checking whether a fix is available yet, and who needs a package

When a finding names a package, two questions decide what to do:

- **Is a fixed version available right now?**
- **What needs this package?**

Ask the package manager inside a throwaway container, without changing anything.

#### Alpine images (the web image)

```bash
MSYS_NO_PATHCONV=1 docker run --rm --user root --entrypoint sh \
  nginxinc/nginx-unprivileged:stable-alpine \
  -c "apk update > /dev/null && apk policy libxslt && apk info -r libxslt"
```

**Real output from this project:**

```text
libxslt policy:
  1.1.43-r3:
    lib/apk/db/installed
  1.1.43-r4:
    https://dl-cdn.alpinelinux.org/alpine/v3.24/main
libxslt-1.1.43-r3 is required by:
nginx-module-xslt-1.30.6-r1
```

**Understanding the output:**

1. **`1.1.43-r3: lib/apk/db/installed`**
   - The version installed in the image.

2. **`1.1.43-r4: https://.../v3.24/main`**
   - A newer version **available** in the repository: the fix exists.

3. **`is required by: nginx-module-xslt-1.30.6-r1`**
   - The package is there because of an optional nginx module, so it is worth asking whether you use that module at all.

**How to interpret the result:**

- If the fixed version is **not listed**, the fix has not reached the repository yet. Wait and rebuild later.
- If it **is listed** but the image still has the old one, the image was **built before the fix was published**. Rebuild with `--pull --no-cache`.

#### Debian images (the backend image)

The same questions, using `apt`. Run this from the app folder; the image must exist.

```bash
docker run --rm --user root --entrypoint sh mecandjeo-mhc-monitoring:dev \
  -c "apt-get update > /dev/null && apt-cache policy zlib1g && apt-cache rdepends --installed zlib1g"
```

- **`apt-cache policy`** prints the `Installed` and `Candidate` versions. A candidate newer than the installed one means a fix is available.
- **`rdepends --installed`** lists the installed packages that need it.

#### Remove what you do not use

If a flawed package only exists to support something you never use (here, an XML-transformation module of nginx), the best fix is a smaller image that does not contain it.

The `-slim` variant of the nginx image leaves out those optional modules, which removes that class of finding altogether.

**Test a candidate image before adopting it:**

```bash
docker pull nginxinc/nginx-unprivileged:stable-alpine-slim

MSYS_NO_PATHCONV=1 docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache \
  aquasec/trivy:latest image --severity HIGH,CRITICAL --ignore-unfixed \
  nginxinc/nginx-unprivileged:stable-alpine-slim

docker image ls nginxinc/nginx-unprivileged --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
```
---

## 10. Commands cheat sheet

1. **Full scan**
   ```bash
   bash scripts/scan_security.sh
   ```

2. **Gate (fails on findings)**
   ```bash
   bash scripts/scan_security.sh --strict; echo "exit code: $?"
   ```

3. **Include minor findings**
   ```bash
   SEVERITY=LOW,MEDIUM,HIGH,CRITICAL bash scripts/scan_security.sh
   ```

4. **Rebuild with the newest fixes**
   ```bash
   docker compose --env-file .env.docker build --pull --no-cache
   ```

5. **Restart and wait until healthy**
   ```bash
   docker compose --env-file .env.docker up -d --wait
   ```

6. **Who runs the process?**
   ```bash
   docker compose --env-file .env.docker exec crane-app id
   ```

7. **Scan one image or a candidate base image by hand**
   ```bash
   MSYS_NO_PATHCONV=1 docker run --rm \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v trivy-cache:/root/.cache \
     aquasec/trivy:latest image --severity HIGH,CRITICAL --ignore-unfixed IMAGE_NAME
   ```

8. **Trivy on your PC (if installed)**
   ```bash
   trivy image --severity HIGH,CRITICAL --ignore-unfixed mecandjeo-mhc-monitoring:dev
   ```

9. **Is the Compose file valid?**
   ```bash
   docker compose --env-file .env.docker config -q
   ```

## 11. Troubleshooting

1. **`[ERROR] ... (not built ...)`**
   - **Cause:** The image does not exist yet.
   - **Fix:**
     ```bash
     docker compose --env-file .env.docker build
     ```

2. **`TOOMANYREQUESTS` or database download fails**
   - **Cause:** The database host is busy.
   - **Fix:** Retry later, or run:
     ```bash
     export TRIVY_DB_REPOSITORY=public.ecr.aws/aquasecurity/trivy-db
     ```

3. **`[FINDINGS]` on an image that was clean before**
   - **Cause:** New flaws were published.
   - **Fix:** See section 9.

4. **Findings remain after adding the update step**
   - **Cause:** Docker reused a cached layer.
   - **Fix:** Rebuild with `--no-cache`.

5. **`docker compose config -q` complains about `start_interval`**
   - **Cause:** Docker Engine is older than version 25.
   - **Fix:** Update Docker Desktop, or remove the `start_interval` lines.

6. **Path or mount error in the Dockerfile scan**
   - **Cause:** Windows path handling.
   - **Fix:** Use:
     ```bash
     bash scripts/scan_security.sh images
     ```
     Then report the message.

7. **`exit code: 1` from `--strict`**
   - **Cause:** Findings exist.
   - **Fix:** That is the gate working: fix or accept the findings.


## 12. Questions and answers

1. **Why was `sleep 20` too short after restarting the web container?**
   - The first health check runs one `interval` (30 seconds) after start, unless `start_interval` is set.
   - Now it reports healthy in about 5 seconds, and `--wait` or `verify_stack.sh` waits for it.

2. **Why did the `time` of a single-container restart show over a minute?**
   - `--force-recreate` applies to dependencies as well.
   - Add `--no-deps` to touch one container.

3. **Does the script mean the Trivy on my PC is no longer useful?**
   - No. It is the same program, installed instead of containerized.
   - The script just does not use it. See section 6.1.

4. **Why did two different tags give identical findings?**
   - The flaws were in packages Alpine had fixed after the image was built, not in nginx.
   - Updating packages at build time fixes both tags.

5. **Why was the backend image clean, then not?**
   - Flaws are published daily.
   - A clean scan describes one day.

6. **What is the difference between `[FINDINGS]` with default mode and with `--strict`?**
   - The same report.
   - Only the exit code differs:
     - `0` by default (so you can read it).
     - `1` with `--strict` (so a pipeline can stop).

7. **What does `--chown=app:app` do?**
   - It sets the owner of copied files to the user `app` and the group `app`, matching the user the container runs as.

8. **What does `-r` do in `-r requirements.lock`?**
   - It tells pip to read the package list from that file.
   - See section 3.
