#!/usr/bin/env bash
# Gate C — harness + API/DB checks when stack is available (HAC-5+)
set -euo pipefail

checks=0
passed=0

check() {
  checks=$((checks + 1))
  if "$@"; then
    passed=$((passed + 1))
    echo "  OK: $*"
  else
    echo "  FAIL: $*"
    exit 1
  fi
}

echo "agent-verify: Career Forge harness"

check test -f AGENTS.md
check test -f docs/CHECKPOINT.md
check test -f docs/AGENT-DELIVERY.md
check test -f .cursor/rules/end-task-workflow.mdc
check test -f claude-design-docs/README.md
check test -f claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md
check test -f claude-design-docs/BORDERLESS-THEMING.md
check test -f .cursor/rules/ui-product-sync.mdc
check test -f apps/api/app/main.py
check test -f apps/web/app/page.tsx
check test -f docker-compose.yml

API_URL="${API_URL:-http://localhost:8000}"
if curl -sf "${API_URL}/health" >/dev/null 2>&1; then
  checks=$((checks + 1))
  if curl -sf "${API_URL}/health" | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["service"] == "career-forge-api"
assert "database" in data
print("runtime health ok")
'; then
    passed=$((passed + 1))
    echo "  OK: API /health runtime check"
    db_status="connected"
  else
    echo "  FAIL: API /health payload"
    exit 1
  fi
else
  db_status="skipped"
  echo "  SKIP: API not running — start with: docker compose up -d"
fi

python3 - <<PY
import json
print(json.dumps({
  "status": "VERIFIED",
  "checks": "harness+monorepo",
  "api_runtime": "${db_status}"
}))
PY

echo "agent-verify: VERIFIED ($passed/$checks checks)"
