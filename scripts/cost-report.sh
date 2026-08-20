#!/usr/bin/env bash
# CAR-43 production cost report — Postgres graph_runs rollup (+ optional LangSmith).
# CAR-7 ./scripts/cost-gate.sh remains the synthetic gate runner.
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

echo "== cost-report (production analytics) =="
cd "${ROOT}/apps/backend"
exec "$PY" -m scripts.cost_report "$@"
