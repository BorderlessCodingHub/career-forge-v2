#!/usr/bin/env bash
set +e
input=$(cat)
loop_count=0
if command -v python3 >/dev/null 2>&1; then
  loop_count=$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("loop_count", 0))' 2>/dev/null || echo 0)
fi
if [ "$loop_count" != "0" ]; then echo '{}'; exit 0; fi
MSG='If you completed a Linear issue: end-task-workflow — set Done in Linear, update docs/STATUS.md and docs/ROADMAP.md. Otherwise reply DONE.'
if command -v python3 >/dev/null 2>&1; then
  MSG="$MSG" python3 - <<'PY'
import json, os
print(json.dumps({"followup_message": os.environ["MSG"]}))
PY
  exit 0
fi
escaped="${MSG//\\/\\\\}"
escaped="${escaped//\"/\\\"}"
printf '{"followup_message":"%s"}\n' "$escaped"
