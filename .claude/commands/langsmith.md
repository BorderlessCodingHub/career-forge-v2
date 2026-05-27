# LangSmith Trace Inspection

Debug LLM behavior by inspecting LangSmith traces for Career Forge graphs.

## Prerequisites

- `.env` must have `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT`
- LangSmith CLI installed: `curl -fsSL https://cli.langsmith.com/install.sh | sh`
- Helper script: `./scripts/langsmith-env.sh` (sources `.env` automatically)

## Common operations

### List recent traces
```
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --last-n-minutes 60 --format pretty
```

### Filter by errors
```
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --error --format pretty
```

### Filter by latency (slow runs)
```
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --min-latency 5000 --format pretty
```

### Get trace details with hierarchy
```
./scripts/langsmith-env.sh trace get <trace-id> --full --show-hierarchy
```
This shows the GraphExecutor tree: graph → nodes → LLM calls.

### Filter by graph name
Career Forge graph names:
- `diagnosis_interview` — CTRR adaptive diagnosis
- `roadmap_forge` — Live Roadmap Forge (SSE timeline)
- `validation` — Mastery validation
- `mock_interview` — Mock interview loop
- `mentor` — Contextual mentor

```
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --name "roadmap_forge" --format pretty
```

### JSON output (machine-readable)
```
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --format json
```

## Rules

1. Always source `.env` first (the helper script does this)
2. Prefer `--show-hierarchy` for GraphExecutor trees
3. Check traces BEFORE changing prompts or graph logic
4. Never commit `LANGSMITH_API_KEY`

## Input
Describe what LLM behavior you want to inspect, or provide a trace ID.
