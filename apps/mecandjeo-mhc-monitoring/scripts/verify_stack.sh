#!/usr/bin/env bash
# One-command health check of the whole local stack, layer by layer: containers, web server, API, database migrations,
# security (non-root) and a real login. Prints PASS or FAIL for each check and exits with a failure code if any check fails.
# The exit code is what lets a pipeline (CI/CD) stop automatically when something is wrong.
#
# Run from apps/mecandjeo-mhc-monitoring:   bash scripts/verify_stack.sh        (add --e2e to also run the browser journey)
#
# Deliberately no "set -e": every check must run so that you see ALL the problems at once, not just the first.
set -uo pipefail

RUN_E2E=false
case "${1:-}" in
  --e2e) RUN_E2E=true ;;
  -h | --help) sed -n '2,8p' "$0"; exit 0 ;;
esac

ENV_FILE="${ENV_FILE:-.env.docker}"
PASS=0
FAIL=0
# Right after a start, containers report "starting" until their first health check passes. Wait up to this long.
WAIT_SECONDS="${WAIT_SECONDS:-60}"
POLL_SECONDS="${POLL_SECONDS:-2}"

# Read one KEY=value setting from the env file (strips Windows line endings; empty if missing).
env_value() { { grep -E "^$1=" "$ENV_FILE" 2>/dev/null || true; } | tail -1 | cut -d= -f2- | tr -d '\r'; }

# Ports and the admin login come from .env.docker, with the usual defaults.
APP_PORT="${APP_PORT:-$(env_value APP_PORT)}"; APP_PORT="${APP_PORT:-8004}"
WEB_PORT="${WEB_PORT:-$(env_value WEB_PORT)}"; WEB_PORT="${WEB_PORT:-8080}"
ADMIN_EMAIL="${ADMIN_EMAIL:-$(env_value BOOTSTRAP_ADMIN_EMAIL)}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-$(env_value BOOTSTRAP_ADMIN_PASSWORD)}"
APP_URL="http://localhost:$APP_PORT"
WEB_URL="http://localhost:$WEB_PORT"
COMPOSE=(docker compose --env-file "$ENV_FILE")

# Record one result.
pass() { printf '[PASS] %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '[FAIL] %s\n       what to try: %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

# check <name> <what to try> <command...>: passes when the command succeeds (exit code 0).
check() {
  local name="$1" hint="$2"
  shift 2
  if "$@" > /dev/null 2>&1; then pass "$name"; else fail "$name" "$hint"; fi
}

# ---- small questions the checks ask (each one succeeds or fails) ----

# The container's own health report (set by the healthcheck in docker-compose.yml): healthy, unhealthy or starting.
# It is empty when the container is stopped or has no health check.
health_of() { docker inspect --format '{{.State.Health.Status}}' "$1" 2>/dev/null; }

# The container is healthy right now.
is_healthy() { [ "$(health_of "$1")" = "healthy" ]; }

# Right after "docker compose up" a container can still be "starting". Give it time instead of reporting a false failure.
wait_while_starting() {
  local waited=0 name starting
  while [ "$waited" -lt "$WAIT_SECONDS" ]; do
    starting=""
    for name in crane-db crane-app crane-web; do
      [ "$(health_of "$name")" = "starting" ] && starting="$starting $name"
    done
    [ -z "$starting" ] && return 0
    printf 'Waiting for:%s (still starting, %ss of %ss)\n' "$starting" "$waited" "$WAIT_SECONDS"
    sleep "$POLL_SECONDS"
    waited=$((waited + POLL_SECONDS))
  done
}

# A one-off job is finished when it has stopped with exit code 0.
job_succeeded() { [ "$(docker inspect --format '{{.State.Status}} {{.State.ExitCode}}' "$1" 2>/dev/null)" = "exited 0" ]; }

# The program inside the container must not run as root (user id 0).
runs_as_non_root() {
  local uid
  uid="$(docker exec "$1" id -u 2>/dev/null)"
  [ -n "$uid" ] && [ "$uid" != "0" ]
}

# The API answers {"status":"ok"} at the given address.
answers_ok() { curl -s "$1" | grep -q '"status":"ok"'; }

# The web container's own address answers with HTTP 200.
status_is_200() { [ "$(curl -s -w '\n%{http_code}' "$1" | tail -n 1)" = "200" ]; }

# Alembic (the migration tool) reports the database is at the latest revision.
migrations_at_head() { "${COMPOSE[@]}" run --rm --no-deps -T crane-migrate alembic current 2>&1 | grep -q '(head)'; }

# Alembic reports no difference between the database and the models.
database_matches_models() {
  "${COMPOSE[@]}" run --rm --no-deps -T crane-migrate alembic check 2>&1 | grep -q 'No new upgrade operations detected'
}

# The packages inside the API image are exactly the ones recorded in requirements.lock (the image was built from the lock).
# The messages some Docker versions print on Windows are filtered out: only "name==version" lines are compared.
image_matches_lock() {
  [ -f requirements.lock ] || return 1
  diff \
    <("${COMPOSE[@]}" run --rm --no-deps -T crane-app pip --disable-pip-version-check freeze 2> /dev/null \
        | tr -d '\r' | grep -E '^[A-Za-z0-9_.-]+==' | sort) \
    <(grep -E '^[A-Za-z0-9_.-]+==' requirements.lock | sort)
}

# Log in as the admin through the web server and print the token (empty when the login fails).
get_token() {
  curl -s -X POST "$WEB_URL/api/auth/login" -H "Content-Type: application/json" \
    -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" \
    | grep -oE '"access_token": ?"[^"]+"' | head -n 1 | sed -E 's/"access_token": ?"([^"]+)"/\1/'
}

# The lookup values (work types, areas, cranes) are readable with the token from get_token.
lookups_served() { curl -s -H "Authorization: Bearer $TOKEN" "$WEB_URL/api/lookups" | grep -q '"cranes"'; }

# The Playwright journey passes (it needs the e2e folder to be installed; see docs).
browser_tests_pass() { (cd e2e && npm test); }

# ---- the checks ----

echo "Checking the stack (web $WEB_URL, API $APP_URL) ..."
echo

if ! docker info > /dev/null 2>&1; then
  echo "[FAIL] Docker is not reachable"
  echo "       what to try: start Docker Desktop and wait until it says the engine is running"
  exit 2
fi

wait_while_starting
echo "Containers"
check "database container is healthy" "docker compose --env-file $ENV_FILE logs crane-db --tail 20" is_healthy crane-db
check "migration job finished with exit code 0" "docker compose --env-file $ENV_FILE logs crane-migrate" job_succeeded crane-migrate
check "API container is healthy" "docker compose --env-file $ENV_FILE logs crane-app --tail 30" is_healthy crane-app
check "web container is healthy" "docker compose --env-file $ENV_FILE logs crane-web --tail 30" is_healthy crane-web

echo
echo "Web server and API"
check "web server answers its own health address" "is the web container running? check the port $WEB_PORT" status_is_200 "$WEB_URL/healthz"
check "API answers directly on port $APP_PORT" "is the API container healthy?" answers_ok "$APP_URL/health"
check "API answers through the web server (proxy)" "check frontend/nginx.conf and that crane-app is healthy" answers_ok "$WEB_URL/health"

echo
echo "Database"
check "migrations are at the latest revision" "run: docker compose --env-file $ENV_FILE run --rm crane-migrate alembic upgrade head" migrations_at_head
check "database matches the models (no drift)" "see docs/PROJECT-PHASES/Phase-10.2-Database-Migrations-Explained.md, section 13" database_matches_models

echo
echo "Security"
check "API container does not run as root" "check the USER line in Dockerfile" runs_as_non_root crane-app
check "web container does not run as root" "use the nginx-unprivileged image in frontend/Dockerfile" runs_as_non_root crane-web

echo
echo "Reproducibility"
check "API image contains exactly the versions in requirements.lock" "rebuild: docker compose --env-file $ENV_FILE build --no-cache crane-app  (regenerate the lock with: bash scripts/update_lock.sh)" image_matches_lock

echo
echo "End to end"
TOKEN="$(get_token)"
check "admin can log in through the web server" "check BOOTSTRAP_ADMIN_* in $ENV_FILE and the API log" test "${#TOKEN}" -gt 100
check "lookup values are served with that login" "check the API log for errors" lookups_served

if [ "$RUN_E2E" = true ]; then
  echo
  echo "Browser journey (Playwright)"
  check "browser tests pass" "cd e2e && npm run report" browser_tests_pass
fi

echo
printf 'Result: %d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]