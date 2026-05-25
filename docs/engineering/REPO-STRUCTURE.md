# Repository structure — Career Forge (canonical)

> **Navigation:** [AGENTS.md](../AGENTS.md) · [AGENT-LIFECYCLE.md](./AGENT-LIFECYCLE.md)

Last updated: **HAC-31** — professional domain-oriented scaffold.

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
        ├── schemas/             # Pydantic structured outputs (HAC-7)
        │   ├── diagnosis.py
        │   ├── forge.py
        │   ├── validation.py
        │   └── planning.py
        ├── agents/              # LangChain runners
        ├── graphs/              # LangGraph state machines ONLY
        │   └── state.py         # SkillGraphState TypedDict
        ├── streaming/           # SSE adapters
        ├── services/            # Business logic, GraphPatch merge
        ├── api/                 # Thin HTTP routers
        └── fixtures/            # Example JSON contracts
```

### Layer rules

| Layer | May import from | Must NOT |
|-------|-----------------|----------|
| `api/` | services, streaming, schemas | agents, graphs directly |
| `streaming/` | graphs, schemas | db models |
| `graphs/` | schemas, agents | FastAPI |
| `services/` | db, schemas | HTTP |
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
    │   │   └── forge/
    │   └── (artifact)/
    │       └── roadmap/
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
5. **`make smoke` passes** — harness + structure + optional stack health

See also [end-task-workflow](../.cursor/rules/end-task-workflow.mdc) § Self-critique.
