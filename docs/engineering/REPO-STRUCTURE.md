# Repository structure — Career Forge (canonical)

> **Navigation:** [AGENTS.md](../AGENTS.md) · [AGENT-LIFECYCLE.md](./AGENT-LIFECYCLE.md) · [EXECUTION-FLOW.md](./EXECUTION-FLOW.md) · [AI-EXECUTION.md](./AI-EXECUTION.md)

Last updated: **HAC-51** — Sprint 6 + deploy hardening docs sync.

## Root layout

```
/
├── apps/
│   ├── backend/          # FastAPI — package: career_forge
│   └── frontend/         # Next.js 14 App Router
├── data/
│   └── roadmap.json      # Skill catalog seed (repo root)
├── docs/
├── claude-design-docs/
├── scripts/
│   ├── agent-verify.sh
│   └── smoke-stack.sh
├── docker-compose.yml
├── docker-compose.prod.yml
├── deploy/
├── Makefile
└── .env.example
```

**Legacy paths removed:** `apps/api/`, `apps/web/` — do not reintroduce.

---

## Backend (`apps/backend/`)

Python package name: **`career_forge`** (import path under `src/`).

```
apps/backend/
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── alembic.ini
├── alembic/
├── scripts/
│   └── seed.py
├── tests/
└── src/
    └── career_forge/
        ├── __init__.py
        ├── main.py              # FastAPI app factory
        ├── config.py
        ├── db/
        │   ├── session.py       # ONLY db entry — no database.py duplicate
        │   ├── base.py
        │   └── models/
        │       └── graph_run.py # GraphRunRecord → graph_runs (Postgres canonical store)
        ├── schemas/             # Pydantic structured outputs (HAC-7)
        │   ├── diagnosis.py
        │   ├── forge.py
        │   ├── validation.py
        │   └── planning.py
        ├── ai/                  # Unified AI layer (HAC-32)
        │   ├── factory.py       # AgentFactory — register/get by name
        │   ├── executor.py      # GraphExecutor — astream_events v2
        │   ├── run.py           # GraphRun entity + GraphRunStore
        │   ├── registry.py      # graph name → builder
        │   ├── recording.py     # persist events into GraphRun
        │   ├── streaming/
        │   │   ├── sse.py       # SSE wire format
        │   │   └── events.py    # LangChain → RoadmapForgeEvent
        │   ├── graphs/
        │   │   ├── base.py      # BaseGraphBuilder protocol
        │   │   ├── state.py     # SkillGraphState TypedDict
        │   │   ├── diagnosis.py
        │   │   ├── diagnosis_interview.py
        │   │   ├── mock_interview.py
        │   │   ├── roadmap_forge.py
        │   │   └── validation.py
        │   ├── agents/          # Non-graph LLM (mentor)
        │   └── prompts/         # Prompt templates
        ├── services/            # Business logic, GraphPatch merge
        ├── api/                 # Thin HTTP routers
        └── fixtures/            # Example JSON contracts
```

### AI layer rules (HAC-32)

| Module | Responsibility |
|--------|----------------|
| `ai/factory.py` | `factory.get("roadmap_forge")` → configured runnable |
| `ai/executor.py` | **Single** code path: `astream_events` v2 → record OR stream |
| `ai/run.py` | `GraphRun` entity + `GraphRunStore` (Postgres canonical; InMemory dev fallback) |
| `ai/streaming/` | SSE + event normalization only — no graph logic |
| `ai/graphs/` | LangGraph builders + `SkillGraphState` |
| `ai/agents/` | Non-graph agents (mentor chat) |

**Self-critique:** No duplicate streaming/recording logic outside `ai/executor.py` and `ai/streaming/`.

Canonical execution docs: [EXECUTION-FLOW.md](./EXECUTION-FLOW.md) (E2E tree + dispatch) · [AI-EXECUTION.md](./AI-EXECUTION.md) (GraphExecutor internals)

### Layer rules

| Layer | May import from | Must NOT |
|-------|-----------------|----------|
| `api/` | services, ai (executor/factory/run), schemas | graphs directly |
| `ai/streaming/` | schemas | db models |
| `ai/graphs/` | schemas, prompts | FastAPI |
| `ai/executor.py` | factory, recording, streaming.events | HTTP |
| `services/` | db, schemas, ai (invoke only) | HTTP, duplicate streaming |
| `db/` | — | business logic |

---

## Frontend (`apps/frontend/`)

```
apps/frontend/
├── package.json
├── Dockerfile
├── next.config.mjs
├── tailwind.config.ts
└── src/
    ├── app/                     # Next App Router
    │   ├── layout.tsx
    │   ├── globals.css
    │   ├── (setup)/
    │   │   ├── page.tsx
    │   │   ├── onboarding/
    │   │   │   └── edit/
    │   │   └── forge/
    │   │       └── complete/
    │   └── (artifact)/
    │       ├── roadmap/
    │       ├── validate/
    │       └── report/
    ├── components/
    │   ├── ui/
    │   ├── layout/
    │   ├── roadmap/
    │   ├── forge/
    │   ├── diagnosis/
    │   └── streaming/
    ├── lib/
    │   ├── api-client.ts
    │   └── sse.ts
    └── types/
        └── contracts.ts
```

---

## Self-critique checklist (before merge)

Agents MUST scan before marking an issue Done:

1. **No duplicate modules** — single `db/session.py`; no parallel schema or utils folders outside domain tree
2. **Structure matches this doc** — run `tree apps/backend/src/career_forge apps/frontend/src` and diff mentally
3. **No orphan files** — every new `.py`/`.tsx` lives under a domain folder above
4. **No legacy references** — `grep -r 'apps/api\|apps/web'` returns nothing outside git history
5. **No duplicate streaming** — grep for `astream_events` / SSE formatters only under `ai/`
6. **`make smoke` passes** — harness + structure + optional stack health

See also [end-task-workflow](../.cursor/rules/end-task-workflow.mdc) § Self-critique.
