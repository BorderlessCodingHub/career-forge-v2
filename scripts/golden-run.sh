#!/usr/bin/env bash
# CAR-18 — Pedro golden scoring helper (coverage refresh or --live forge).
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

echo "== golden-run (CAR-18) =="
cd "${ROOT}/apps/backend"
export PYTHONPATH="${PYTHONPATH:-}:src"
exec "$PY" -m scripts.golden_run "$@"
