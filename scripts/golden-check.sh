#!/usr/bin/env bash
# CAR-18 — deterministic golden suite check (no OpenAI).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PY="${ROOT}/.venv-backend-tests/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="${PYTHON:-python3}"
fi

echo "== golden-check (CAR-18) =="
cd "${ROOT}/apps/backend"
export PYTHONPATH="${PYTHONPATH:-}:src"
exec "$PY" -m scripts.golden_check "$@"
