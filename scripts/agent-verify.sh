#!/usr/bin/env bash
# Gate C stub — extend with real API/DB checks as stack lands (HAC-5+)
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

python3 - <<'PY'
import json
print(json.dumps({
  "status": "VERIFIED",
  "checks": "harness-bootstrap",
  "note": "Extend with API/Postgres checks when apps/api exists"
}))
PY

echo "agent-verify: VERIFIED ($passed/$checks harness checks)"
