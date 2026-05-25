---
name: langsmith-inspect
description: Use LangSmith CLI to inspect LLM traces/runs for Career Forge debugging. Use when debugging diagnosis interview, forge SSE, mentor flows, or any upstream LLM execution.
---

# LangSmith inspect

Inspect LangSmith traces and runs for Career Forge LLM flows (`GraphExecutor`, LangGraph).

Helper script: [`scripts/langsmith-env.sh`](../../scripts/langsmith-env.sh)

---

## Credentials (mandatory)

**Always load from repo `.env`** before any CLI call. Never print or commit API keys.

```bash
cd /path/to/HB01-2026_soft-push
set -a && source .env && set +a
```

Or use the helper (recommended):

```bash
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --last-n-minutes 60
```

Default project: `$LANGSMITH_PROJECT` (`career-forge` from `.env.example`).

If auth fails, verify `LANGSMITH_API_KEY` is set in `.env` (not `.env.example`). Do **not** ask the user for the key when `.env` exists — read it via the helper.

CLI install (if missing): `curl -fsSL https://cli.langsmith.com/install.sh | sh` → `~/.local/bin/langsmith`

---

## Key commands

Recent traces (human-readable):

```bash
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --last-n-minutes 60 --format pretty
```

Full trace hierarchy (GraphExecutor / nested runs):

```bash
./scripts/langsmith-env.sh trace get <trace-id> --project "$LANGSMITH_PROJECT" --full --show-hierarchy --format pretty
```

Recent LLM runs with metadata:

```bash
./scripts/langsmith-env.sh run list --project "$LANGSMITH_PROJECT" --run-type llm --include-metadata --last-n-minutes 60
```

Single run detail:

```bash
./scripts/langsmith-env.sh run get <run-id> --full
```

Filters:

| Filter | Flag |
|--------|------|
| Errors only | `--error` |
| Slow traces (≥5s) | `--min-latency 5` |
| By graph/name | `--name diagnosis_interview` |

---

## Output formats

- `--format pretty` — tables, trees, highlighted JSON (default; use for human review)
- `--format json` — machine-readable (pipe to `jq`, scripts, agents)

---

## Career Forge graph names

Search traces/runs by `--name` or tags when debugging:

| Graph / flow | Typical `--name` |
|--------------|------------------|
| Adaptive diagnosis | `diagnosis_interview` |
| Live Roadmap Forge | `forge`, `roadmap_forge` |
| Mentor chat | `mentor` |
| Mastery validation | `validation` |

Prefer **`trace get … --show-hierarchy`** for GraphExecutor flows — nested LLM/tool nodes appear as a tree.

---

## Workflow

1. Reproduce the bug locally (`make up`, hit the API route or UI flow).
2. `./scripts/langsmith-env.sh` — confirm project + API key status.
3. List recent traces (`--last-n-minutes 60`); add `--error` or `--min-latency 5` if needed.
4. Drill into trace/run IDs; compare inputs, outputs, and token usage.
5. Cross-reference backend `GraphRun` / `run_id` with LangSmith trace ID when available.

---

## Env status (no args)

```bash
./scripts/langsmith-env.sh
```

Prints repo path, project, key status (length only), and CLI version.
