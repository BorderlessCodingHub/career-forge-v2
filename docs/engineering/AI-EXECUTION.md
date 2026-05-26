# AI execution architecture — Career Forge

> **Navigation:** [EXECUTION-FLOW.md](./EXECUTION-FLOW.md) · [REPO-STRUCTURE.md](./REPO-STRUCTURE.md) · [CHECKPOINT.md](../CHECKPOINT.md)

Canonical reference for how graphs/agents run, stream, and persist events.

Last updated: **HAC-51**

---

## Overview

All AI flows (diagnosis, roadmap forge, validation, mentor) share one execution stack:

```
api/forge.py  ──►  GraphExecutor  ──►  AgentFactory.get(name)
                         │                    │
                         │                    └──► ai/graphs/* or ai/agents/*
                         │
                         ├── astream_events v2 (always)
                         ├── ai/recording.py → GraphRun
                         └── ai/streaming/ → SSE (when stream=True)
```

**Rule:** Never call LangGraph/LangChain streaming directly from `api/` or per-graph modules. Always go through `GraphExecutor`.

---

## GraphRun entity

Defined in `career_forge/ai/run.py`:

| Field | Purpose |
|-------|---------|
| `id` | UUID for this execution |
| `graph_name` | Registry key (`diagnosis`, `roadmap_forge`, …) |
| `user_id` | Owning user |
| `status` | `pending` → `running` → `completed` \| `failed` |
| `input` | Request payload |
| `output` | Final structured result |
| `raw_events` | Full astream_events v2 payloads (audit/debug) |
| `normalized_events` | Client-facing event dicts |
| `error` | Failure message when `status=failed` |
| timestamps | `created_at`, `updated_at`, `completed_at` |

**Store (canonical):** Postgres via `GraphRunRecord` → `graph_runs` table (Alembic `002_graph_runs`). Implement `PostgresGraphRunStore` satisfying the `GraphRunStore` protocol. **`InMemoryGraphRunStore`** remains dev/test fallback only (pytest, local smoke without DB).

**LangGraph checkpointer (canonical):** Postgres checkpointer pattern (`PostgresSaver` / `langgraph-checkpoint-postgres`) — graph internal state between nodes. Injected into builders via `AgentFactory`. Same Postgres instance; separate checkpoint tables from `graph_runs`.

End-to-end flow: [EXECUTION-FLOW.md](./EXECUTION-FLOW.md) § Persistence — Postgres checkpointer.

---

## AgentFactory

```python
from career_forge.ai.factory import get_agent_factory

factory = get_agent_factory()
runnable = factory.get("roadmap_forge")  # names match schema modules
```

Registered names:

| Name | Builder | Issue |
|------|---------|-------|
| `diagnosis` | `build_diagnosis_graph` | HAC-8 |
| `diagnosis_interview` | `build_diagnosis_interview_graph` | HAC-43 |
| `roadmap_forge` | `build_roadmap_forge_graph` | HAC-18 |
| `validation` | `build_validation_graph` | HAC-10 |
| `mock_interview` | `build_mock_interview_graph` | HAC-14 |
| `mentor` | `build_mentor_agent` | HAC-13 |

Extend via `factory.register(name, builder_fn)`.

---

## GraphExecutor

Single class in `career_forge/ai/executor.py`:

```python
result = await executor.execute(run, stream=False)   # → GraphRunResult
events = await executor.execute(run, stream=True)    # → AsyncIterator[dict]
```

### Internal flow (both modes)

1. Resolve runnable via `AgentFactory.get(run.graph_name)`
2. Set `run.status = running`, persist
3. Iterate `runnable.astream_events(input, version="v2")`
4. For each LangChain event:
   - Append to `run.raw_events` (`recording.record_raw_event`)
   - Normalize via `streaming.events.normalize_langchain_event`
   - Append to `run.normalized_events` when non-`None`
   - **If `stream=True`:** yield normalized dict immediately
5. `finalize_run(run)` — set output/error, `completed_at`
6. Persist run to store

### Stream vs collect

| Mode | HTTP | Client receives | GraphRun |
|------|------|-----------------|----------|
| `stream=False` | `POST /forge` | Full JSON result after completion | All events recorded |
| `stream=True` | `GET /forge/{run_id}/stream` or `GET /forge/stream` | SSE lines via `streaming/sse.py` | Same recording path |

Same loop, same recording — only the client-facing delivery differs.

---

## astream_events v2

GraphExecutor **always** calls:

```python
async for event in runnable.astream_events(input_data, version="v2"):
    ...
```

LangChain v2 event shape (simplified):

```json
{
  "event": "on_chain_stream",
  "name": "emit_forge_event",
  "run_id": "...",
  "data": { "chunk": { "forge_event": { "type": "reasoning_delta", ... } } }
}
```

`ai/streaming/events.py` maps these to:

- **Forge:** `RoadmapForgeEvent` schema (`reasoning_delta`, `graph_ready`, …)
- **Other graphs:** `graph_complete` wrapper with structured output

Production path uses LangGraph builders through `ai/registry.py` for diagnosis, diagnosis interview, roadmap forge, validation and mock interview; mentor remains a non-graph agent runnable.

---

## HTTP surface (`api/forge.py`)

| Method | Path | Behavior |
|--------|------|----------|
| `POST` | `/forge` | Create `GraphRun`, execute collect, return `{ run_id, events, output }` |
| `GET` | `/forge/stream` | Demo SSE — ephemeral run, stream mock forge |
| `GET` | `/forge/{run_id}/stream` | Re-execute stored run with `stream=True` → SSE |

Other AI-backed routers already follow this pattern (`diagnosis`, `diagnosis_interview`, `validation`, `mock_interview`, `mentor`).

---

## Implementing a new graph (checklist)

1. Add builder in `ai/graphs/<name>.py` returning a `GraphRunnable`
2. Register in `ai/registry.py`
3. Add prompts under `ai/prompts/` if needed
4. **Do not** add streaming logic — GraphExecutor handles it
5. Wire thin route in `api/` that creates `GraphRun` and calls executor

---

## Current follow-ups

- [ ] Replace `MockGraphRunnable` with compiled LangGraph graphs (HAC-8/10/18)
- [ ] Wire `PostgresGraphRunStore` as production default (replace module-level `InMemoryGraphRunStore`)
- [ ] Inject LangGraph `PostgresSaver` checkpointer in graph builders
- [ ] LangSmith trace IDs on `GraphRun`
- [ ] Replay stored `raw_events` without re-execution (optional)

---

*HB01-2026 · Programadores Sem Pátria*
