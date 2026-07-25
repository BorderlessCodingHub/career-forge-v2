#!/usr/bin/env bash
# CAR-7 synthetic cost gate — measure forge/diagnosis cost → Yuri report.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export FORGE_STREAM_DELAY_SEC=0
export GRAPH_RUN_STORE="${GRAPH_RUN_STORE:-memory}"

PY="${ROOT}/.venv-backend-tests/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="${PYTHON:-python3}"
fi

echo "== CAR-7 cost gate =="
cd "${ROOT}/apps/backend"
exec "$PY" -m scripts.cost_gate "$@"
