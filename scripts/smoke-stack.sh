#!/usr/bin/env bash
# Stack smoke — docker compose + health checks (HAC-5)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

API_URL="${BACKEND_URL:-${API_URL:-http://localhost:8000}}"
WEB_URL="${FRONTEND_URL:-${WEB_URL:-http://localhost:${WEB_HOST_PORT:-3000}/career-forge}}"

wait_for_url() {
  local url="$1"
  local label="$2"
  local attempts="${3:-30}"
  local i=1
  while [ "$i" -le "$attempts" ]; do
    if curl -sf "$url" >/dev/null 2>&1; then
      echo "  OK: $label reachable at $url"
      return 0
    fi
    sleep 2
    i=$((i + 1))
  done
  echo "  FAIL: $label not reachable at $url"
  return 1
}

echo "smoke-stack: validating compose file"
docker compose config -q

if ! curl -sf "${API_URL}/health" >/dev/null 2>&1; then
  echo "smoke-stack: starting docker compose (--wait)"
  export WEB_HOST_PORT="${WEB_HOST_PORT:-3300}"
  export WEB_URL="http://localhost:${WEB_HOST_PORT}/career-forge"
  docker compose up -d --build --wait
fi

echo "smoke-stack: API /health"
curl -sf "${API_URL}/health" | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data.get("service") == "career-forge-api", data
assert data.get("status") in ("ok", "degraded"), data
print("  OK: health payload valid:", data)
'

echo "smoke-stack: OpenAPI /docs"
curl -sf "${API_URL}/docs" | grep -q "Swagger UI" && echo "  OK: /docs serves OpenAPI UI"

wait_for_url "${WEB_URL}" "frontend home" 90

echo "smoke-stack: STACK OK"
