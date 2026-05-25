---
name: agent-verify
description: Gate C — run make agent-verify for API + Postgres proof before merge. Extend scripts/agent-verify.sh for new behavior.
---

# Agent verify (Gate C)

[docs/AGENT-DELIVERY.md § Gate C](../../docs/AGENT-DELIVERY.md)

## Run

```bash
make smoke
make agent-verify
```

Exit 0 + `"status": "VERIFIED"` = pass.

## Extend

Every feature PR that mutates API or Postgres must add checks to `scripts/agent-verify.sh`.

Planned checks (as stack lands):

- `GET /health`
- Diagnosis endpoint returns valid JSON
- Forge SSE emits typed events
- Skill graph state persisted
- Validation creates evidence row
