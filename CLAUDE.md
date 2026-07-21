# Career Forge — Claude Code context

**Career Forge v2** — AI-native learning system for BASE/PSP: adaptive skill graph, Live Roadmap Forge with streaming, AI-driven mastery validation.

Borderless Labs · `labs.borderlesscoding.com/career-forge` · Linear team **CAR** · plan: [docs/V2-PLAN.md](./docs/V2-PLAN.md)

## Stack

```
apps/frontend/     Next.js + TS + Tailwind (App Router)
apps/backend/      FastAPI + Pydantic + SQLAlchemy
PostgreSQL         skill graph state, validations, profiles, graph_runs
LangGraph          diagnosis, diagnosis_interview, roadmap_forge, validation, mock_interview, mentor
LangChain          astream_events v2 via GraphExecutor
LangSmith          traces per GraphRun
```

## Repo structure

```
apps/
  backend/src/career_forge/
    api/            thin routes — no business logic
    services/       orchestration layer
    ai/
      executor.py   GraphExecutor — SINGLE astream_events v2 path
      factory.py    AgentFactory.get("graph_name") → runnable
      registry.py   graph registration
      run.py        GraphRun entity + store
      streaming/    SSE + event normalization ONLY
      graphs/       graph builders (diagnosis, forge, validation…)
      agents/       agent builders (mentor…)
    db/
      session.py    ONLY DB session entry point
      models/       SQLAlchemy models
    schemas/        Pydantic schemas
  frontend/
    app/
      (setup)/      goal, onboarding, forge routes
      (artifact)/   roadmap, validate, report routes
    components/     organized by domain
data/roadmap.json   static skill catalog
scripts/            agent-verify.sh, langsmith-env.sh
docs/               engineering, product, decisions
claude-design-docs/ prototype + design tokens
```

## Commands

| Command | When |
|---------|------|
| `make up` / `make down` / `make status` | Local docker stack |
| `make test` | Backend pytest — before merge |
| `make smoke` | Full harness + stack health |
| `make seed` | Seed catalog + demo user Ana |
| `make agent-verify` | Gate C — structure + `/health` |

## Custom commands (Claude Code)

| Command | Purpose | Cursor equivalent |
|---------|---------|-------------------|
| `/project:start-task` | Start Linear issue, create branch | linear-delivery-workflow rule |
| `/project:qa-gate` | Triple QA gate before merge | dual-qa-gate skill |
| `/project:agent-verify` | Gate C verification | agent-verify skill |
| `/project:end-task` | Post-merge checklist | end-task-workflow rule |
| `/project:smoke` | Session smoke test | end-session-smoke rule |
| `/project:debug` | Runtime debugging checklist | local-debug skill |
| `/project:langsmith` | LangSmith trace inspection | langsmith-inspect skill |
| `/project:sync-ui` | Sync UI product docs | ui-product-sync skill |

---

## Rules

### Git workflow

- Branch format: `CAR-XX-title-slug` (strip any `username/` prefix from Linear)
- One issue = one branch = one merge
- Target 200–500 LOC per merge
- Before merge: triple QA gate (see below)
- After merge: run `/project:end-task`
- No GitHub↔Linear automation — Linear status transitions are **manual**

### Triple QA gate (mandatory before merge)

Three gates must pass: **SHIP + PASS + VERIFIED**

| Gate | Tool | Verdict | What |
|------|------|---------|------|
| A — Evaluator | Code review (readonly) | SHIP / FIX / SPLIT | git diff, scope = single CAR issue, structure compliance |
| B — UI test | Playwright or manual | PASS / FAIL | Demo flows: goal, forge timeline, graph reveal, validation |
| C — Agent verify | `make agent-verify` | VERIFIED / FAILED | API + Postgres structure proof |

Execution order: A+B parallel → C → merge → end-task

When to skip gates:
- API/DB only (no UI): skip B
- Docs-only: skip all
- .cursor/ or .claude/ config: A only

### Parallel dispatch

When 2+ issues are classified as **[P]** (parallel) with satisfied dependencies, launch all subagents in a single message. Classifications:
- **P** — parallel: independent, can run concurrently
- **S** — sequential: depends on prior issue output
- **B** — blocker: blocks entire batch

### AI execution layer

Golden rules for `apps/backend/ai/`:

1. **GraphExecutor only** — all graphs execute via `executor.execute(run, stream=True|False)`. No per-graph streaming.
2. **AgentFactory resolution** — `factory.get("name")` returns configured runnable. No direct graph imports in routes.
3. **Single astream_events v2 path** — `executor.py` owns the event loop. `streaming/` normalizes SSE events.
4. **Postgres canonical** — `GraphRunRecord` for audit trail, LangGraph `PostgresSaver` for checkpoint state. Both Postgres.
5. **No duplicate streaming** — streaming logic exists ONLY in `ai/executor.py` and `ai/streaming/`.

Anti-patterns:
- ❌ Direct `graph.astream()` calls outside executor
- ❌ New streaming helpers outside `ai/streaming/`
- ❌ `InMemoryStore` in production paths
- ❌ Per-graph SSE event types (use `streaming/events.py` registry)

New graph checklist: builder in `graphs/`, register in `registry.py`, add prompts, thin API route, do NOT add streaming logic.

### Diagnosis interview (CTRR)

When touching `apps/backend/ai/graphs/diagnosis*` or `apps/frontend/app/(setup)/onboarding`:

- Read [ADR-001](./docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md) + [DIAGNOSIS-INTERVIEW.md](./docs/product/DIAGNOSIS-INTERVIEW.md) first
- CTRR rubric (Conceptual / Technical / Readiness / Resourcefulness)
- Max 2 questions per turn, accumulative transcript
- Frontend is a **dumb renderer** — logic lives in the graph, not the UI
- Anti-patterns: static pills, mock diagnosis, demo toggles, hardcoded question lists

### CV ingest

When touching `apps/backend/services/cv*`:

- PDF-only extraction
- Optional LLM → `CvSignals`
- Fail-open design: missing CV must not block diagnosis

### UI product sync

When touching `apps/frontend/`, `claude-design-docs/`, Tailwind, or CSS:

- Before UI work: read [PRODUCT-SOURCE-OF-TRUTH.md](./claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md)
- After UI work: if paradigm changed, run `/project:sync-ui`
- Never weaken P0 features (Forge timeline stream, validation, adaptive roadmap)

### End-of-session smoke

Before ending any session that touched `apps/`, `scripts/`, infra, Makefile, or Docker:
- Run `make smoke`
- If `make smoke` isn't available yet, run `make test` or verify `/health`

### Local debugging

On any runtime error (failed to fetch, CORS, Docker, API errors):
1. `docker compose ps` — check stack health
2. `docker compose logs <service>` — inspect logs
3. Verify CORS (`CORS_ORIGINS` in `.env`)
4. API smoke: `curl http://localhost:8000/health`
5. Environment checklist: `OPENAI_API_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, `WEB_HOST_PORT`
6. No mock fallbacks — fix the real issue

### LangSmith inspection

Before changing prompts, graphs, or streaming:
1. `./scripts/langsmith-env.sh` — confirm credentials
2. List recent traces: `./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --last-n-minutes 60`
3. Drill into trace: `./scripts/langsmith-env.sh trace get <id> --full --show-hierarchy`

Graph names: `diagnosis_interview`, `roadmap_forge`, `validation`, `mock_interview`, `mentor`

---

## Session bootstrap

At the start of a session involving implementation work, read in order:

1. This file (CLAUDE.md) / [AGENTS.md](./AGENTS.md)
2. [V2-PLAN.md](./docs/V2-PLAN.md) — phases, locked decisions
3. [ROADMAP.md](./docs/ROADMAP.md) — current phase, CAR issues, [P]/[S]/[B]
4. [STATUS.md](./docs/STATUS.md) — parity matrix, last merge
5. [CHECKPOINT.md](./docs/CHECKPOINT.md) — product, stack, wow features
6. Issue scope via Linear MCP (`CAR-XX`)
7. [claude-design-docs/](./claude-design-docs/) when doing frontend work

## Documentation index

| Need | Read |
|------|------|
| v2 plan | [V2-PLAN.md](./docs/V2-PLAN.md) |
| Product overview | [CHECKPOINT.md](./docs/CHECKPOINT.md) |
| Current work | [ROADMAP.md](./docs/ROADMAP.md), [STATUS.md](./docs/STATUS.md) |
| AI runtime | [EXECUTION-FLOW.md](./docs/engineering/EXECUTION-FLOW.md), [AI-EXECUTION.md](./docs/engineering/AI-EXECUTION.md) |
| Repo structure | [REPO-STRUCTURE.md](./docs/engineering/REPO-STRUCTURE.md) |
| Deploy Labs | [DEPLOY-LABS-MANUAL.md](./docs/DEPLOY-LABS-MANUAL.md) |
| Diagnosis spec | [DIAGNOSIS-INTERVIEW.md](./docs/product/DIAGNOSIS-INTERVIEW.md), [ADR-001](./docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md) |
| Delivery gates | [AGENT-DELIVERY.md](./docs/AGENT-DELIVERY.md) |
| Agent lifecycle | [AGENT-LIFECYCLE.md](./docs/engineering/AGENT-LIFECYCLE.md) |
| UI design | [PRODUCT-SOURCE-OF-TRUTH.md](./claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md) |

## API surface

| Prefix | Key endpoints |
|--------|---------------|
| `/health` | Health probe |
| `/diagnosis/interview/start`, `/{session_id}/turn` | Multi-turn CTRR diagnosis |
| `/forge`, `/forge/stream`, `/forge/{run_id}/stream` | Forge run + SSE |
| `/roadmap/`, `/roadmap/sync` | Steady-state trail |
| `/validation/questions`, `/validation` | Mastery validation |
| `/mentor/context`, `/mentor` | Contextual mentor |
| `/mentor-report` | Evidence report |
| `/mock-interview/questions`, `/mock-interview` | Mock interview + recalibration |

## Frontend routes

| Route | Purpose |
|-------|---------|
| `(setup)/` | Goal entry |
| `(setup)/onboarding` | Adaptive diagnosis interview |
| `(setup)/onboarding/edit` | Editable diagnosis |
| `(setup)/forge` | Live forge timeline SSE |
| `(setup)/forge/complete` | Post-forge transition |
| `(artifact)/roadmap` | Vertical roadmap |
| `(artifact)/validate` | Mastery validation |
| `(artifact)/report` | Mentor report |

## Environment

Required in `.env` (copy from `.env.example`):
- `OPENAI_API_KEY` — required for diagnosis, forge, validation
- `DATABASE_URL` — Postgres (Docker fills it in)
- `CORS_ORIGINS` — must include the frontend URL
- `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_API_URL` — frontend → API
- `WEB_HOST_PORT` — Next.js port on the host
- `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` — optional, LLM observability
