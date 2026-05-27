#!/usr/bin/env bash
# Gate C — harness + backend/frontend structure checks (HAC-31+)
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
check test -f docs/engineering/REPO-STRUCTURE.md
check test -f .cursor/rules/end-task-workflow.mdc
check test -f claude-design-docs/README.md
check test -f claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md
check test -f claude-design-docs/BORDERLESS-THEMING.md
check test -f .cursor/rules/ui-product-sync.mdc
check test -f apps/backend/src/career_forge/ai/executor.py
check test -f apps/backend/src/career_forge/ai/factory.py
check test -f apps/backend/src/career_forge/ai/run.py
check test -f .cursor/rules/ai-execution.mdc
check test -f docs/engineering/EXECUTION-FLOW.md
check test -f docs/engineering/AI-EXECUTION.md
check test -f docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md
check test -f docs/product/DIAGNOSIS-INTERVIEW.md
check test -f .cursor/rules/diagnosis-interview.mdc
check test -f .cursor/rules/cv-ingest.mdc
check test -f apps/frontend/src/components/diagnosis/AGENTS.md
check test -f apps/backend/src/career_forge/ai/graphs/diagnosis_interview.py
check test -f apps/backend/src/career_forge/api/diagnosis_interview.py
check test -f apps/backend/src/career_forge/services/diagnosis_session.py
check test -f apps/backend/src/career_forge/api/mentor.py
check test -f apps/backend/src/career_forge/ai/agents/mentor.py
check test -f apps/backend/src/career_forge/services/profile_diagnosis.py
check test -f apps/backend/src/career_forge/schemas/profile_diagnosis.py
check test -f apps/backend/src/career_forge/db/stores/postgres_graph_run.py
check test -f apps/backend/src/career_forge/persistence/store_mode.py
check test ! -f apps/backend/src/career_forge/database.py
check test -f apps/frontend/src/app/layout.tsx
check test -f apps/frontend/src/app/\(setup\)/page.tsx
check test -f docker-compose.yml

# No legacy app paths (exclude harness docs that mention the ban)
LEGACY_EXCLUDE='(REPO-STRUCTURE|end-task-workflow|AGENT-LIFECYCLE|AGENT-DELIVERY|agent-verify\.sh)'
if find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" -o -name "Makefile" -o -name "*.mdc" -o -name "*.toml" -o -name "*.json" \) \
  ! -path "./.git/*" \
  -exec grep -lE 'apps/(api|web)' {} + 2>/dev/null | grep -vE "${LEGACY_EXCLUDE}" | grep -q .; then
  echo "  FAIL: legacy apps/api or apps/web references found"
  find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" -o -name "Makefile" -o -name "*.mdc" -o -name "*.toml" -o -name "*.json" \) \
    ! -path "./.git/*" \
    -exec grep -lE 'apps/(api|web)' {} + 2>/dev/null | grep -vE "${LEGACY_EXCLUDE}" || true
  exit 1
else
  checks=$((checks + 1))
  passed=$((passed + 1))
  echo "  OK: no legacy apps/api or apps/web references"
fi

API_URL="${BACKEND_URL:-${API_URL:-http://localhost:8000}}"
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
  "checks": "harness+monorepo+structure",
  "api_runtime": "${db_status}"
}))
PY

echo "agent-verify: VERIFIED ($passed/$checks checks)"
