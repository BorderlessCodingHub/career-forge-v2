#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DB_USER="${POSTGRES_USER:-careerforge}"
DB_PASSWORD="${POSTGRES_PASSWORD:-careerforge}"
DB_NAME="${POSTGRES_DB:-careerforge}"
DB_HOST="${POSTGRES_HOST:-127.0.0.1}"
DB_PORT="${POSTGRES_PORT:-55432}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${ROOT}/.venv-backend-tests"
TEST_COMPOSE_PROJECT="${TEST_COMPOSE_PROJECT:-career-forge-tests}"

compose_cmd() {
  docker compose -p "$TEST_COMPOSE_PROJECT" "$@"
}

export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}}"

echo "== Backend tests =="
echo "Using DATABASE_URL host=${DB_HOST} port=${DB_PORT} db=${DB_NAME}"
echo "Using compose project: ${TEST_COMPOSE_PROJECT}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required for make test bootstrap" >&2
  exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "python3 is required for make test bootstrap" >&2
  exit 1
fi

echo "Starting postgres service for tests..."
compose_cmd down -v >/dev/null 2>&1 || true
export POSTGRES_HOST_PORT="$DB_PORT"
compose_cmd up -d postgres --wait

echo "Waiting for postgres readiness..."
ATTEMPTS=30
for i in $(seq 1 "$ATTEMPTS"); do
  if compose_cmd exec -T postgres pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    echo "Postgres is ready."
    break
  fi
  if [ "$i" -eq "$ATTEMPTS" ]; then
    echo "postgres readiness timeout after ${ATTEMPTS} attempts" >&2
    exit 1
  fi
  sleep 2
done

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install -q -r apps/backend/requirements.txt pytest httpx

echo "Running Alembic migrations on test database..."
(
  cd apps/backend
  PYTHONPATH=src alembic upgrade head
)

echo "Running pytest..."
(
  cd apps/backend
  PYTHONPATH=src python -m pytest -q
)

if [ "${TEST_KEEP_DB:-false}" != "true" ]; then
  compose_cmd down -v >/dev/null 2>&1 || true
fi
