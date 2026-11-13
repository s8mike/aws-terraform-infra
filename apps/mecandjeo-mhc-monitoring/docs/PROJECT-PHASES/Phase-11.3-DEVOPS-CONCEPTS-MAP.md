<!-- DEVOPS-CONCEPTS-MAP.md: a plain-language map of the DevOps ideas used in this project, each linked to the file where it lives, a command to try it, and the roadmap phase that builds on it. -->

# DevOps Concepts Map

This project is a way to learn DevOps tools on a real application. This page lists each idea in plain words, shows **where it lives in the project**, gives a **command to try it**, and says which **later phase builds on it**. Keep it open while you work; the entries are in a sensible learning order.

Commands are for **Git Bash**, run from `apps/mecandjeo-mhc-monitoring`.

## Contents

1. Containers and images
2. Docker Compose
3. Web serving
4. Databases in operations
5. Security
6. Reproducibility
7. Verification
8. Version control and pipelines
9. The roadmap, seen as skills

---

## 1. Containers and images

1. **Container**
   - **In plain words:** A running, isolated program with everything it needs.
   - **Where it lives here:** `crane-app`, `crane-web`, `crane-db`.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker ps -a
     ```
   - **Builds on in:** 13 (ECS), 15 (Kubernetes).

2. **Image**
   - **In plain words:** The frozen recipe result a container starts from.
   - **Where it lives here:** `mecandjeo-mhc-monitoring:dev`, `mecandjeo-mhc-web:dev`.
   - **Try it:**
     ```bash
     docker image ls
     ```
   - **Builds on in:** 13 (pushed to a registry).

3. **Dockerfile**
   - **In plain words:** The written recipe for building an image.
   - **Where it lives here:** `Dockerfile`, `frontend/Dockerfile`.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker build crane-app
     ```
   - **Builds on in:** 14 (built by the pipeline).

4. **Layer and build cache**
   - **In plain words:** Each Dockerfile step is saved and reused when unchanged.
   - **Where it lives here:** The order of `COPY` and `RUN` lines.
   - **Try it:** Rebuild twice and watch the second build be fast. `build --no-cache` ignores the saved layers.
   - **Builds on in:** 14.

5. **Multi-stage build**
   - **In plain words:** Build in one image, ship only the result in another.
   - **Where it lives here:** `frontend/Dockerfile` (Node builds, nginx serves).
   - **Try it:** Run `docker image ls` and compare sizes.
   - **Builds on in:** 14.

6. **Base image**
   - **In plain words:** The image your image starts from (`python:3.12-slim`).
   - **Where it lives here:** The `FROM` lines.
   - **Try it:**
     ```bash
     grep -n "^FROM" Dockerfile frontend/Dockerfile
     ```
   - **Builds on in:** 14 (automatic updates).

7. **Tag**
   - **In plain words:** A movable label on an image (`stable-alpine`).
   - **Where it lives here:** `FROM nginxinc/nginx-unprivileged:stable-alpine`.
   - **Try it:** Compare tags in the scan: an old tag produced 61 findings.
   - **Builds on in:** 14.

8. **Digest**
   - **In plain words:** An exact, unchangeable fingerprint of an image.
   - **Where it lives here:** Not used yet.
   - **Try it:**
     ```bash
     docker image ls --digests
     ```
   - **Builds on in:** 14.

9. **Volume**
   - **In plain words:** Storage that outlives the container.
   - **Where it lives here:** The PostgreSQL data volume.
   - **Try it:** `down` keeps it; `down -v` erases it.
   - **Builds on in:** 12 (RDS replaces it).

10. **Port mapping**
    - **In plain words:** Making a container's port reachable from your PC.
    - **Where it lives here:** `8004:8004` and `8080:8080`.
    - **Try it:**
      ```bash
      curl http://localhost:8080/healthz
      ```
    - **Builds on in:** 12 (load balancer).


## 2. Docker Compose

1. **Compose file**
   - **In plain words:** One file describing all the services and how they connect.
   - **Where it lives here:** `docker-compose.yml`.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker config -q
     ```
     Silent when valid.
   - **Builds on in:** 13 (ECS task definitions), 15.

2. **Service**
   - **In plain words:** One named piece of the stack.
   - **Where it lives here:** `crane-db`, `crane-migrate`, `crane-app`, `crane-web`.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker ps -a
     ```
   - **Builds on in:** 15.

3. **Service discovery**
   - **In plain words:** Containers find each other by name.
   - **Where it lives here:** nginx forwards to `crane-app:8004`; the API reaches `crane-db`.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker exec crane-web wget -qO- http://crane-app:8004/health
     ```
   - **Builds on in:** 15 (Kubernetes Services).

4. **Environment file**
   - **In plain words:** Settings kept out of the code.
   - **Where it lives here:** `.env.docker` (ignored by Git), `.env.docker.example` (committed).
   - **Try it:**
     ```bash
     git check-ignore -v .env.docker
     ```
   - **Builds on in:** 12 (secrets in AWS), 17.

5. **Health check**
   - **In plain words:** A scheduled question: "are you OK?"
   - **Where it lives here:** `healthcheck:` blocks.
   - **Try it:**
     ```bash
     docker inspect --format '{{.State.Health.Status}}' crane-app
     ```
   - **Builds on in:** 13 (ALB checks), 15 (probes).

6. **Start order and conditions**
   - **In plain words:** Wait for a dependency to be healthy or finished.
   - **Where it lives here:** `depends_on:` with `service_healthy` and `service_completed_successfully`.
   - **Try it:** Stop `crane-db` and watch what refuses to start.
   - **Builds on in:** 13.

7. **`up --wait`**
   - **In plain words:** Start and wait until everything is healthy.
   - **Where it lives here:** Used instead of `sleep`.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker up -d --wait
     ```
   - **Builds on in:** 14.

8. **One-off job**
   - **In plain words:** A container that does one task and exits.
   - **Where it lives here:** `crane-migrate` (`Exited (0)` is success).
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker ps -a
     ```
   - **Builds on in:** 13 (an ECS task before deployment).

9. **Restart policy**
   - **In plain words:** What to do when a container stops.
   - **Where it lives here:** `restart:` lines.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker ps -a
     ```
   - **Builds on in:** 13.

## 3. Web serving

1. **Reverse proxy**
   - **In plain words:** A front door that forwards requests to the right service.
   - **Where it lives here:** nginx in `crane-web` forwards `/api/` to the API.
   - **Try it:**
     ```bash
     curl http://localhost:8080/health
     ```
     Answered by the API through nginx.
   - **Builds on in:** 12 (load balancer, CloudFront).

2. **Same-origin serving**
   - **In plain words:** The browser sees one address, so no CORS settings are needed.
   - **Where it lives here:** Port 8080 serves both the site and `/api`.
   - **Try it:** Open browser developer tools and select the Network tab.
   - **Builds on in:** 12.

3. **Single-page app fallback**
   - **In plain words:** Unknown paths return `index.html` so React shows the right screen.
   - **Where it lives here:** `try_files` in `frontend/nginx.conf`.
   - **Try it:** Refresh the browser on `/operator`.
   - **Builds on in:** 12.

4. **Cache headers**
   - **In plain words:** Tell browsers how long to keep files.
   - **Where it lives here:** `/assets/` cached one year.
   - **Try it:**
     ```bash
     curl -sI <asset-url>
     ```
     Look for `max-age=31536000`.
   - **Builds on in:** 12 (CloudFront).

5. **Static build**
   - **In plain words:** The site is built once into plain files.
   - **Where it lives here:** `npm run build` creates `dist/`.
   - **Try it:**
     ```bash
     ls frontend/dist
     ```
     Run after a build.
   - **Builds on in:** 14.


## 4. Databases in operations

1. **Migration**
   - **In plain words:** A versioned, repeatable change to the database structure.
   - **Where it lives here:** `migrations/versions/0001_baseline.py`.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker run --rm --no-deps -T crane-migrate alembic current
     ```
   - **Builds on in:** 13 (run before each deployment).

2. **Schema versus data**
   - **In plain words:** The structure of the tables versus the rows in them.
   - **Where it lives here:** Migrations change the schema only.
   - **Try it:** Read `docs/PROJECT-PHASES/Phase-10.2-Database-Migrations-Explained.md`.
   - **Builds on in:** 13.

3. **Drift check**
   - **In plain words:** Do the code's models match the real tables?
   - **Where it lives here:** `alembic check`, and a check in `verify_stack.sh`.
   - **Try it:**
     ```bash
     bash scripts/verify_stack.sh
     ```
   - **Builds on in:** 14.

4. **Idempotent job**
   - **In plain words:** Safe to run again with no extra effect.
   - **Where it lives here:** The bootstrap and the seed script.
   - **Try it:** Run `bash scripts/seed_demo_data.sh` twice.
   - **Builds on in:** 13.

5. **Backup**
   - **In plain words:** A copy of the data you can restore.
   - **Where it lives here:** A `pg_dump` taken before the Phase 11 rebuild.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker exec -T crane-db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql
     ```
     **Important:** Contains password hashes; delete it when done.
   - **Builds on in:** 12 (RDS backups).

## 5. Security

1. **Least privilege**
   - **In plain words:** Run with the fewest powers needed.
   - **Where it lives here:** `USER app` and `USER 101`.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker exec crane-app id
     ```
     Not root.
   - **Builds on in:** 12 (IAM roles), 15.

2. **CVE**
   - **In plain words:** A public ID for one known flaw.
   - **Where it lives here:** Reported by Trivy.
   - **Try it:**
     ```bash
     bash scripts/scan_security.sh
     ```
   - **Builds on in:** 14, 18.

3. **Vulnerability scanner**
   - **In plain words:** Compares what is inside an image with known flaws.
   - **Where it lives here:** Trivy in `scripts/scan_security.sh`.
   - **Try it:**
     ```bash
     bash scripts/scan_security.sh images
     ```
   - **Builds on in:** 14 (pipeline gate).

4. **Misconfiguration scan**
   - **In plain words:** Checks files for risky settings.
   - **Where it lives here:** Trivy `config` (it also scanned your Terraform).
   - **Try it:**
     ```bash
     bash scripts/scan_security.sh config
     ```
   - **Builds on in:** 12 (Terraform), 14.

5. **Security gate**
   - **In plain words:** A check that fails the build when something serious is found.
   - **Where it lives here:** `--strict` and the exit code.
   - **Try it:**
     ```bash
     bash scripts/scan_security.sh --strict; echo "exit code: $?"
     ```
   - **Builds on in:** 14.

6. **Documented exception**
   - **In plain words:** Accepting a finding on purpose, with a written reason.
   - **Where it lives here:** `.trivyignore`.
   - **Try it:**
     ```bash
     cat .trivyignore
     ```
   - **Builds on in:** 14.

7. **Secret handling**
   - **In plain words:** Passwords never go into Git.
   - **Where it lives here:** `.env.docker` is ignored; examples hold placeholders.
   - **Try it:**
     ```bash
     git check-ignore -v .env.docker
     ```
   - **Builds on in:** 12 (AWS secrets), 17.

8. **Patching**
   - **In plain words:** Applying fixes for known flaws.
   - **Where it lives here:** `apt-get upgrade`, `apk upgrade` in the Dockerfiles.
   - **Try it:** Run `build --pull --no-cache`, then scan.
   - **Builds on in:** 14, 18.


## 6. Reproducibility

1. **Lock file**
   - **In plain words:** The exact version of every package.
   - **Where it lives here:** `requirements.lock`, `package-lock.json`.
   - **Try it:**
     ```bash
     head -n 8 requirements.lock
     ```
   - **Builds on in:** 14.

2. **Direct versus transitive dependency**
   - **In plain words:** Packages you chose versus packages those need.
   - **Where it lives here:** 11 chosen, 25 installed.
   - **Try it:** Read `docs/PROJECT-PHASES/Phase-11.2-DEPENDENCY-LOCKING.md`, section 3.
   - **Builds on in:** 14.

3. **Pinning**
   - **In plain words:** Fixing a version on purpose.
   - **Where it lives here:** `bcrypt==4.0.1` in `requirements.txt`.
   - **Try it:**
     ```bash
     grep -n "==" requirements.txt
     ```
   - **Builds on in:** 14.

4. **Clean install**
   - **In plain words:** Install exactly what the lock says.
   - **Where it lives here:** `npm ci` in `frontend/Dockerfile`.
   - **Try it:**
     ```bash
     cd frontend && npm ci
     ```
   - **Builds on in:** 14.

5. **Reviewable update**
   - **In plain words:** An update you can read before accepting.
   - **Where it lives here:** `git diff requirements.lock`.
   - **Try it:**
     ```bash
     bash scripts/update_lock.sh
     git diff requirements.lock
     ```
   - **Builds on in:** 14 (automatic update requests).

6. **Rollback**
   - **In plain words:** Return to the previous working state.
   - **Where it lives here:** Restore the old lock and rebuild.
   - **Try it:**
     ```bash
     git checkout -- requirements.lock
     ```
   - **Builds on in:** 17 (Git decides what runs).

7. **Image matches lock**
   - **In plain words:** Proof the built image is what was recorded.
   - **Where it lives here:** A check in `verify_stack.sh`.
   - **Try it:**
     ```bash
     bash scripts/verify_stack.sh
     ```
   - **Builds on in:** 14.

## 7. Verification

1. **Unit test**
   - **In plain words:** Checks one rule or component in isolation.
   - **Where it lives here:** pytest (71), Vitest (107).
   - **Try it:**
     ```bash
     python -m pytest tests -q
     ```
   - **Builds on in:** 14.

2. **End-to-end test**
   - **In plain words:** Drives the whole system as a user would.
   - **Where it lives here:** Playwright (6) in `e2e/`.
   - **Try it:**
     ```bash
     cd e2e && npm test
     ```
   - **Builds on in:** 14.

3. **Smoke check**
   - **In plain words:** A quick "is it alive and sane?"
   - **Where it lives here:** `scripts/verify_stack.sh`.
   - **Try it:**
     ```bash
     bash scripts/verify_stack.sh
     ```
   - **Builds on in:** 13 (after each deployment).

4. **Exit code**
   - **In plain words:** The number a program ends with: 0 is success.
   - **Where it lives here:** Every script.
   - **Try it:**
     ```bash
     echo "exit code: $?"
     ```
   - **Builds on in:** 14.

5. **A check that can fail**
   - **In plain words:** A verification you have seen fail is one you can trust.
   - **Where it lives here:** The lock check caught an older image.
   - **Try it:** Stop `crane-web` and run the stack check.
   - **Builds on in:** 18.

6. **Test data hygiene**
   - **In plain words:** Tests clean up after themselves.
   - **Where it lives here:** `E2E-` names, `cleanup-test-data.sql`.
   - **Try it:** Read `docs/PROJECT-PHASES/Phase-11.4-PLAYWRIGHT-GUIDE.md`.
   - **Builds on in:** 14.

## 8. Version control and pipelines

1. **Commit**
   - **In plain words:** A saved, named snapshot of changes.
   - **Where it lives here:** Local commits, one app at a time.
   - **Try it:**
     ```bash
     git log --oneline -5
     ```
   - **Builds on in:** 14.

2. **Local versus remote**
   - **In plain words:** Your copy versus the one on GitHub.
   - **Where it lives here:** `origin/main`.
   - **Try it:**
     ```bash
     git status
     ```
   - **Builds on in:** 14.

3. **Conventional commit**
   - **In plain words:** A commit message style: `type(scope): message`.
   - **Where it lives here:** `feat(mhc-monitoring): ...`.
   - **Try it:**
     ```bash
     git log --oneline
     ```
   - **Builds on in:** 14.

4. **Staging only what you mean**
   - **In plain words:** Add one folder, never everything.
   - **Where it lives here:** `git add .` inside the app folder.
   - **Try it:**
     ```bash
     git status --short .
     ```
   - **Builds on in:** 14.

5. **CI/CD pipeline**
   - **In plain words:** Automatic tests, builds and deployments on every change.
   - **Where it lives here:** Planned: GitHub Actions.
   - **Try it:** Read `docs/PROJECT-PHASES/Phase-11.5-SCRIPTS-REFERENCE.md`, section 11.
   - **Builds on in:** 14.

6. **Infrastructure as code**
   - **In plain words:** Cloud resources described in files.
   - **Where it lives here:** Terraform in `infra/`.
   - **Try it:**
     ```bash
     trivy config infra/
     ```
     If Trivy is installed.
   - **Builds on in:** 12.

7. **GitOps**
   - **In plain words:** The Git repository decides what runs.
   - **Where it lives here:** Planned: Argo CD.
   - **Builds on in:** 17.

8. **Observability**
   - **In plain words:** Seeing what the running system does.
   - **Where it lives here:** Planned: metrics, logs, alerts.
   - **Try it:**
     ```bash
     docker compose --env-file .env.docker logs crane-app --tail 20
     ```
   - **Builds on in:** 18.
---

## 9. The roadmap, seen as skills

1. **Phase 9 — Local readiness**
   - **The DevOps skill it teaches:** Safe start-up, bootstrap, configuration.
   - **What you already practiced:** `.env.docker`, health checks.

2. **Phase 10 — Frontend**
   - **The DevOps skill it teaches:** Building what gets deployed.
   - **What you already practiced:** `npm run build`, tests.

3. **Phase 11 — Full-stack local validation**
   - **The DevOps skill it teaches:** Containers, migrations, hardening, scanning, locks, verification.
   - **What you already practiced:** **Everything on this page.**

4. **Phase 12 — AWS infrastructure**
   - **The DevOps skill it teaches:** Infrastructure as code (Terraform): network, ECS, load balancer, RDS, logs.
   - **What you already practiced:** Reading `infra/`, scanning it with Trivy.

5. **Phase 13 — End-to-end deployment**
   - **The DevOps skill it teaches:** Registry (ECR), rolling out, running migrations in the cloud, rollback.
   - **What you already practiced:** `crane-migrate`, `verify_stack.sh`, locked builds.

6. **Phase 14 — Frontend CI/CD**
   - **The DevOps skill it teaches:** A pipeline that tests, builds, scans and publishes.
   - **What you already practiced:** The tests, `scan_security.sh --strict`, exit codes.

7. **Phase 15 — Kubernetes foundations**
   - **The DevOps skill it teaches:** Running the same containers in a cluster.
   - **What you already practiced:** Health checks as probes, non-root containers.

8. **Phase 16 — Helm packaging**
   - **The DevOps skill it teaches:** Packaging and configuring deployments.
   - **What you already practiced:** Settings in `.env.docker`.

9. **Phase 17 — Argo CD GitOps**
   - **The DevOps skill it teaches:** Git as the source of truth for what runs.
   - **What you already practiced:** Locks, small reviewable commits.

10. **Phase 18 — Observability and reliability**
    - **The DevOps skill it teaches:** Metrics, dashboards, alerts.
    - **What you already practiced:** Health checks, logs, repeated scans.

11. **Phase 19 — Demonstration readiness**
    - **The DevOps skill it teaches:** Presenting the whole system.
    - **What you already practiced:** The verification checklist.
