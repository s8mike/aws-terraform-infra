#!/usr/bin/env bash
# Security scan of this project with Trivy, a free scanner that runs as a container (nothing to install):
#   config - checks the Dockerfiles for risky settings (fast)
#   images - checks the built images for known vulnerabilities (CVEs) in the operating system and the packages inside
# Default: show the findings and exit 0. With --strict: exit 1 when serious findings exist (how a pipeline uses it).
# Exit code 2 means the scan itself could not run (Docker down, image not built, scanner error).
#
# Usage, from apps/mecandjeo-mhc-monitoring:   bash scripts/scan_security.sh [--strict] [config|images]
# Optional settings: SEVERITY (default HIGH,CRITICAL)   TRIVY_IMAGE (default aquasec/trivy:latest)
set -uo pipefail

STRICT=false
MODE=all
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=true ;;
    config | images | all) MODE="$arg" ;;
    -h | --help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg (try --help)" >&2; exit 2 ;;
  esac
done

ENV_FILE="${ENV_FILE:-.env.docker}"
SEVERITY="${SEVERITY:-HIGH,CRITICAL}"
TRIVY_IMAGE="${TRIVY_IMAGE:-aquasec/trivy:latest}"
# Trivy ends with this code when it found something (its own errors end with 1), so the two cases can be told apart.
FINDINGS_CODE=5
FINDINGS=0
ERRORS=0

# Read one KEY=value setting from the env file (strips Windows line endings; empty if missing).
env_value() { { grep -E "^$1=" "$ENV_FILE" 2>/dev/null || true; } | tail -1 | cut -d= -f2- | tr -d '\r'; }

# The two images built by docker-compose.yml, named the same way the compose file names them.
IMAGE_NAME="$(env_value IMAGE_NAME)"; IMAGE_NAME="${IMAGE_NAME:-mecandjeo-mhc-monitoring}"
IMAGE_TAG="$(env_value IMAGE_TAG)"; IMAGE_TAG="${IMAGE_TAG:-dev}"
WEB_IMAGE_NAME="$(env_value WEB_IMAGE_NAME)"; WEB_IMAGE_NAME="${WEB_IMAGE_NAME:-mecandjeo-mhc-web}"
IMAGES=("$IMAGE_NAME:$IMAGE_TAG" "$WEB_IMAGE_NAME:$IMAGE_TAG")

# The project folder as Docker needs to see it: a Windows-style path under Git Bash, the normal path elsewhere.
PROJECT_DIR="$(pwd -W 2>/dev/null || pwd)"

# Run the Trivy container. The named volume "trivy-cache" keeps the downloaded vulnerability database between runs.
# MSYS_NO_PATHCONV stops Git Bash on Windows from rewriting the Linux-style paths passed to Docker.
# "-e TRIVY_DB_REPOSITORY" passes your own setting through (only if you set it), for when the default database
# host is busy: export TRIVY_DB_REPOSITORY=public.ecr.aws/aquasecurity/trivy-db
trivy_run() { MSYS_NO_PATHCONV=1 docker run --rm -e TRIVY_DB_REPOSITORY -v trivy-cache:/root/.cache "$@"; }

# Scan the Dockerfiles (settings only; folders full of other people's code are skipped).
scan_config() {
  trivy_run -v "$PROJECT_DIR:/project" -w /project "$TRIVY_IMAGE" \
    config --severity "$SEVERITY" --exit-code "$FINDINGS_CODE" \
    --skip-dirs frontend/node_modules --skip-dirs e2e/node_modules --skip-dirs frontend/dist \
    --skip-dirs .venv --skip-dirs venv .
}

# Scan one built image through the Docker socket; only flaws that already have a fix are reported.
scan_image() {
  trivy_run -v /var/run/docker.sock:/var/run/docker.sock "$TRIVY_IMAGE" \
    image --severity "$SEVERITY" --ignore-unfixed --exit-code "$FINDINGS_CODE" "$1"
}

# report <what was scanned> <exit code of the scan>
report() {
  case "$2" in
    0) printf '[CLEAN]    %s\n' "$1" ;;
    "$FINDINGS_CODE") printf '[FINDINGS] %s\n' "$1"; FINDINGS=$((FINDINGS + 1)) ;;
    *) printf '[ERROR]    %s (scanner exit code %s)\n' "$1" "$2"; ERRORS=$((ERRORS + 1)) ;;
  esac
}

if ! docker info > /dev/null 2>&1; then
  echo "[ERROR] Docker is not reachable. Start Docker Desktop and wait until it says the engine is running."
  exit 2
fi

if [ "$MODE" = all ] || [ "$MODE" = config ]; then
  echo "== Dockerfiles (risky settings), severity $SEVERITY"
  scan_config
  report "Dockerfiles in this project" $?
fi

if [ "$MODE" = all ] || [ "$MODE" = images ]; then
  for image in "${IMAGES[@]}"; do
    echo
    echo "== Image $image (known vulnerabilities with a fix available), severity $SEVERITY"
    if ! docker image inspect "$image" > /dev/null 2>&1; then
      report "$image (not built: run docker compose --env-file $ENV_FILE build)" 99
      continue
    fi
    scan_image "$image"
    report "$image" $?
  done
fi

echo
printf 'Result: %d scan(s) with findings, %d error(s)\n' "$FINDINGS" "$ERRORS"
if [ "$ERRORS" -gt 0 ]; then exit 2; fi
if [ "$FINDINGS" -gt 0 ] && [ "$STRICT" = true ]; then exit 1; fi
exit 0