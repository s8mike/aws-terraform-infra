#!/usr/bin/env bash
# Seeds a small demo data set through the public API so the manager screens have something to show.
# Run once on a fresh local database (after "down -v" and "up -d --build"). Needs curl and sed only.
# The admin email and password come from .env.docker (BOOTSTRAP_ADMIN_EMAIL / BOOTSTRAP_ADMIN_PASSWORD),
# so there is nothing to type. Override with ADMIN_EMAIL, ADMIN_PASSWORD, ENV_FILE or BASE if needed.
set -Eeuo pipefail

# If any command fails, say which one instead of exiting silently.
trap 'echo "Stopped at line $LINENO: $BASH_COMMAND" >&2' ERR

BASE="${BASE:-http://localhost:8004}"
ENV_FILE="${ENV_FILE:-.env.docker}"
JSON="Content-Type: application/json"
DEMO_PASSWORD="Securepass123!"

# Read one KEY=value setting from the env file (strips Windows line endings; empty if missing).
env_value() { { grep -E "^$1=" "$ENV_FILE" 2>/dev/null || true; } | tail -1 | cut -d= -f2- | tr -d '\r'; }

ADMIN_EMAIL="${ADMIN_EMAIL:-$(env_value BOOTSTRAP_ADMIN_EMAIL)}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-$(env_value BOOTSTRAP_ADMIN_PASSWORD)}"
if [ -z "$ADMIN_EMAIL" ] || [ -z "$ADMIN_PASSWORD" ]; then
  echo "Admin email or password not found. Run this from the folder that holds $ENV_FILE," >&2
  echo "or set ADMIN_EMAIL and ADMIN_PASSWORD before running." >&2
  exit 1
fi

# Pull one field out of the compact JSON the API returns (no jq needed).
token_of() { sed -E 's/.*"access_token":"([^"]+)".*/\1/'; }
id_of() { sed -E 's/.*"id":([0-9]+).*/\1/'; }

# Thin wrappers: api_post <path> <token> <json>, api_patch <path> <token> <json>, api_login <email> <password>.
api_post() { curl -s -X POST "$BASE$1" -H "$JSON" -H "Authorization: Bearer $2" -d "$3"; }
api_patch() { curl -s -X PATCH "$BASE$1" -H "$JSON" -H "Authorization: Bearer $2" -d "$3"; }
api_login() { curl -s -X POST "$BASE/api/auth/login" -H "$JSON" -d "{\"email\":\"$1\",\"password\":\"$2\"}" | token_of; }

# Stop with a clear message when a value that should be a number (an id) is not one.
require_id() {
  case "$1" in
    '' | *[!0-9]*) echo "Failed: $2 -> $1" >&2; exit 1 ;;
  esac
}

echo "Checking the API at $BASE ..."
if ! curl -s -f "$BASE/health" > /dev/null; then
  echo "The API is not reachable. Start it with: docker compose --env-file .env.docker up -d" >&2
  exit 1
fi

echo "Logging in as $ADMIN_EMAIL ..."
ADMIN_TOKEN=$(api_login "$ADMIN_EMAIL" "$ADMIN_PASSWORD")
if [ "${#ADMIN_TOKEN}" -lt 100 ]; then
  echo "Admin login failed. Check BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD in $ENV_FILE." >&2
  exit 1
fi

# Register operator1; a 409 means the demo data was already created, so stop without changing anything.
STATUS=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/auth/register" -H "$JSON" \
  -d "{\"email\":\"operator1@example.com\",\"full_name\":\"Operator One\",\"password\":\"$DEMO_PASSWORD\",\"role\":\"operator\",\"is_active\":true}" | tail -n 1)
if [ "$STATUS" = "409" ]; then
  echo "operator1 already exists: demo data was already created. Reset with 'down -v' to seed again."
  exit 0
fi
[ "$STATUS" = "201" ] || { echo "Registering operator1 failed with status $STATUS" >&2; exit 1; }

curl -s -X POST "$BASE/api/auth/register" -H "$JSON" \
  -d "{\"email\":\"operator2@example.com\",\"full_name\":\"Operator Two\",\"password\":\"$DEMO_PASSWORD\",\"role\":\"operator\",\"is_active\":true}" > /dev/null
echo "Creating manager1 ..."
api_post /api/admin/users "$ADMIN_TOKEN" \
  "{\"email\":\"manager1@example.com\",\"full_name\":\"Manager One\",\"password\":\"$DEMO_PASSWORD\",\"role\":\"manager\",\"is_active\":true}" > /dev/null

echo "Operator One: shift A on MHC-01 with two completed tasks ..."
OP1=$(api_login operator1@example.com "$DEMO_PASSWORD")
SHIFT1=$(api_post /api/shifts/start "$OP1" '{"mhc_number":"MHC-01","shift_code":"A","started_at":"2026-10-07T06:00:00"}' | id_of)
require_id "$SHIFT1" "operator1 start shift"

# Task 1: Discharging, 60 minutes, one 15-minute delay, 24 containers.
T1=$(api_post /api/task-logs/start "$OP1" "{\"shift_id\":$SHIFT1,\"nature_of_work\":\"discharging\",\"working_area\":\"deck_free_bay\",\"vessel_name\":\"MV Demo\",\"started_at\":\"2026-10-07T06:10:00\"}" | id_of)
require_id "$T1" "operator1 start task 1"
D1=$(api_post /api/delay-logs/start "$OP1" "{\"task_log_id\":$T1,\"delay_type\":\"awaiting_trucks\",\"started_at\":\"2026-10-07T06:30:00\"}" | id_of)
require_id "$D1" "operator1 start delay"
api_patch "/api/delay-logs/$D1/end" "$OP1" '{"ended_at":"2026-10-07T06:45:00"}' > /dev/null
api_patch "/api/task-logs/$T1/end" "$OP1" '{"ended_at":"2026-10-07T07:10:00","container_count":24}' > /dev/null

# Task 2: Loading, 60 minutes, no delay, 30 containers.
T2=$(api_post /api/task-logs/start "$OP1" "{\"shift_id\":$SHIFT1,\"nature_of_work\":\"loading\",\"working_area\":\"underdeck_across_heights\",\"vessel_name\":\"MV Demo\",\"started_at\":\"2026-10-07T07:20:00\"}" | id_of)
require_id "$T2" "operator1 start task 2"
api_patch "/api/task-logs/$T2/end" "$OP1" '{"ended_at":"2026-10-07T08:20:00","container_count":30}' > /dev/null
api_patch "/api/shifts/$SHIFT1/end" "$OP1" '{"ended_at":"2026-10-07T08:30:00"}' > /dev/null

echo "Operator Two: shift B on MHC-02, one completed task, one active task with an active delay ..."
OP2=$(api_login operator2@example.com "$DEMO_PASSWORD")
SHIFT2=$(api_post /api/shifts/start "$OP2" '{"mhc_number":"MHC-02","shift_code":"B","started_at":"2026-10-07T14:00:00"}' | id_of)
require_id "$SHIFT2" "operator2 start shift"

# Task 3: Loading - Empties, 50 minutes, one 20-minute breakdown, 18 containers.
T3=$(api_post /api/task-logs/start "$OP2" "{\"shift_id\":$SHIFT2,\"nature_of_work\":\"loading_empties\",\"working_area\":\"underdeck_free_bay\",\"started_at\":\"2026-10-07T14:10:00\"}" | id_of)
require_id "$T3" "operator2 start task 3"
D3=$(api_post /api/delay-logs/start "$OP2" "{\"task_log_id\":$T3,\"delay_type\":\"breakdown\",\"started_at\":\"2026-10-07T14:30:00\"}" | id_of)
require_id "$D3" "operator2 start delay"
api_patch "/api/delay-logs/$D3/end" "$OP2" '{"ended_at":"2026-10-07T14:50:00"}' > /dev/null
api_patch "/api/task-logs/$T3/end" "$OP2" '{"ended_at":"2026-10-07T15:00:00","container_count":18}' > /dev/null

# Task 4 stays active, with an active rainfall delay, so the live view has something to show.
T4=$(api_post /api/task-logs/start "$OP2" "{\"shift_id\":$SHIFT2,\"nature_of_work\":\"discharging\",\"working_area\":\"port_side\",\"vessel_name\":\"MV Sample\",\"started_at\":\"2026-10-07T15:10:00\"}" | id_of)
require_id "$T4" "operator2 start task 4"
D4=$(api_post /api/delay-logs/start "$OP2" "{\"task_log_id\":$T4,\"delay_type\":\"rainfall\",\"started_at\":\"2026-10-07T15:30:00\"}" | id_of)
require_id "$D4" "operator2 start delay 2"

echo "Done. Sign in with operator1@example.com, operator2@example.com or manager1@example.com (password: $DEMO_PASSWORD)."