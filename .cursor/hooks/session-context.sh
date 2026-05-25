#!/usr/bin/env bash
set +e
read -r _input || true
CONTEXT='Career OS hackathon repo. Read AGENTS.md → docs/ROADMAP.md → docs/STATUS.md → docs/CHECKPOINT.md. Linear status is MANUAL — use end-task-workflow after merge.'
if command -v python3 >/dev/null 2>&1; then
  CONTEXT="$CONTEXT" python3 - <<'PY'
import json, os
print(json.dumps({"additional_context": os.environ["CONTEXT"]}))
PY
  exit 0
fi
escaped="${CONTEXT//\\/\\\\}"
escaped="${escaped//\"/\\\"}"
printf '{"additional_context":"%s"}\n' "$escaped"
