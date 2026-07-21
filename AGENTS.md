# Career Forge — Agent harness (index)

**Career Forge v2** — AI-native learning system for BASE/PSP: adaptive skill graph, Live Roadmap Forge with streaming, AI-driven mastery validation. Deployed at `labs.borderlesscoding.com/career-forge`.

**Stack:** Next.js · FastAPI · PostgreSQL · LangGraph + LangChain + LangSmith  
**Linear:** [Career Forge V2](https://linear.app/career-forge-v2) · team key **`CAR`**

This file is the **table of contents**. Details live under [`docs/`](./docs/README.md) and [`claude-design-docs/`](./claude-design-docs/README.md).

---

## Start here — by task type

| Task | Read in order | Then do |
|------|---------------|---------|
| **Implement a Linear issue** | [V2-PLAN](./docs/V2-PLAN.md) → [ROADMAP](./docs/ROADMAP.md) → [STATUS](./docs/STATUS.md) → [CHECKPOINT](./docs/CHECKPOINT.md) → issue scope → [AGENT-DELIVERY](./docs/AGENT-DELIVERY.md) | Branch `CAR-XX-title-slug` · triple gate · merge · **end-task** |
| **AI / LangGraph work** | [EXECUTION-FLOW](./docs/engineering/EXECUTION-FLOW.md) → [AI-EXECUTION](./docs/engineering/AI-EXECUTION.md) → [REPO-STRUCTURE](./docs/engineering/REPO-STRUCTURE.md) § AI layer | Use `GraphExecutor` + `AgentFactory` — no per-graph streaming |
| **Debug LLM / traces** | [langsmith-inspect skill](./.cursor/skills/langsmith-inspect/SKILL.md) → [langsmith-inspect rule](./.cursor/rules/langsmith-inspect.mdc) | `./scripts/langsmith-env.sh` loads `.env` · inspect traces before changing prompts/graphs |
| **Local runtime / failed to fetch** | [local-debug skill](./.cursor/skills/local-debug/SKILL.md) → [local-debug rule](./.cursor/rules/local-debug.mdc) | Docker logs · CORS · `logs/backend.log` when `ENV=local` |
| **Diagnosis / onboarding AI** | [ADR-001](./docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md) → [DIAGNOSIS-INTERVIEW](./docs/product/DIAGNOSIS-INTERVIEW.md) → [diagnosis-interview rule](./.cursor/rules/diagnosis-interview.mdc) | Multi-turn CTRR · ≤2 Q/turn · FE dumb renderer · soft gate in v2 pilot |
| **Bootstrap / first session** | [V2-PLAN](./docs/V2-PLAN.md) → [ROADMAP](./docs/ROADMAP.md) → [STATUS](./docs/STATUS.md) → [CHECKPOINT](./docs/CHECKPOINT.md) | Paste block below · `make smoke` when apps exist |
| **Understand full application** | [CHECKPOINT](./docs/CHECKPOINT.md) → [engineering/REPO-STRUCTURE](./docs/engineering/REPO-STRUCTURE.md) → [engineering/EXECUTION-FLOW](./docs/engineering/EXECUTION-FLOW.md) | Canonical product + runtime overview |
| **Cloud agent / Linear** | [CURSOR-CLOUD](./docs/CURSOR-CLOUD.md) | Linear Cursor plugin · workspace career-forge-v2 |
| **Agent lifecycle / planning** | [AGENT-LIFECYCLE](./docs/engineering/AGENT-LIFECYCLE.md) → [ROADMAP](./docs/ROADMAP.md) | Classify P/S/B · parallel dispatch for [P] batches |
| **UI from Claude Design** | [PRODUCT-SOURCE-OF-TRUTH](./claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md) → [claude-design-docs/README.md](./claude-design-docs/README.md) | Map prototype → Next.js; sync docs after paradigm change |
| **Delivery / merge** | [AGENT-DELIVERY](./docs/AGENT-DELIVERY.md) → [end-task-workflow](./.cursor/rules/end-task-workflow.mdc) | `SHIP + PASS + VERIFIED` then **manual Done in Linear** |
| **Deploy Labs** | [DEPLOY-LABS-MANUAL](./docs/DEPLOY-LABS-MANUAL.md) | Path `/career-forge` on Labs VPS |

---

## New session — manual bootstrap

Paste as first agent message if hooks unavailable:

```
Repo: career-forge-v2 (Career Forge v2 · Borderless Labs).
Read AGENTS.md → V2-PLAN → ROADMAP → STATUS → CHECKPOINT → EXECUTION-FLOW (AI work).
Pick current ROADMAP phase only. Branch: CAR-XX-title-slug.
Before merge: triple gate (docs/AGENT-DELIVERY.md). make test && make smoke when runtime touched.
After merge: end-task — manually set Linear issue to Done (no GitHub↔Linear automation).
Update docs/STATUS.md + ROADMAP.
```

---

## Subagent Task template (mandatory for parent)

```
Repo: career-forge-v2. Base: origin/main (pull latest).

Read AGENTS.md → docs/V2-PLAN.md → docs/ROADMAP.md → docs/STATUS.md → docs/CHECKPOINT.md before coding.
Scope: single issue CAR-XX only.

Branch: CAR-XX-title-slug
Acceptance: <from Linear get_issue>

Before merge: triple gate — SHIP + PASS + VERIFIED.
After merge: end-task (Linear MCP save_issue state Done + STATUS.md).
Report: merge summary, gate verdicts, blockers.
```

---

## Agent workflow order

```
sessionStart hook
  → AGENTS.md
  → V2-PLAN.md         phases, locked decisions
  → ROADMAP.md         current phase, CAR issues, [P]/[S]/[B]
  → STATUS.md          parity matrix, last merge
  → CHECKPOINT.md      product, stack, wow features
  → issue scope        Linear MCP (CAR-XX)
  → claude-design-docs/  UI intent (when front-end)
      PRODUCT-SOURCE-OF-TRUTH.md first
  → AGENT-DELIVERY.md  triple QA gate
  → end-task-workflow  manual Linear Done
```

Full lifecycle: [docs/engineering/AGENT-LIFECYCLE.md](./docs/engineering/AGENT-LIFECYCLE.md)

---

## Rules & skills

| Resource | Purpose |
|----------|---------|
| [V2-PLAN](./docs/V2-PLAN.md) | Canonical v2 execution plan + decision log |
| [EXECUTION-FLOW](./docs/engineering/EXECUTION-FLOW.md) | E2E tree, parallel dispatch, Postgres checkpointer |
| [AI-EXECUTION](./docs/engineering/AI-EXECUTION.md) | GraphRun, GraphExecutor, AgentFactory, stream vs collect |
| [ai-execution](./.cursor/rules/ai-execution.mdc) | GraphExecutor-only path for AI/LangGraph changes |
| [AGENT-LIFECYCLE](./docs/engineering/AGENT-LIFECYCLE.md) | Session entry → planning → impl → QA → exit |
| [CURSOR-CLOUD](./docs/CURSOR-CLOUD.md) | Cloud bootstrap · Linear plugin |
| [linear-delivery-workflow](./.cursor/rules/linear-delivery-workflow.mdc) | Branch, micro-PR, P/S/B classification |
| [parallel-dispatch](./.cursor/rules/parallel-dispatch.mdc) | **Mandatory** parallel Task launch for [P] batches |
| [end-task-workflow](./.cursor/rules/end-task-workflow.mdc) | **Manual Linear Done** (no GitHub integration) |
| [dual-qa-gate](./.cursor/rules/dual-qa-gate.mdc) | Triple gate summary |
| [agent-delivery-gate](./.cursor/rules/agent-delivery-gate.mdc) | SHIP + PASS + VERIFIED |
| [end-session-smoke](./.cursor/rules/end-session-smoke.mdc) | `make smoke` before ending session |
| [ui-product-sync](./.cursor/rules/ui-product-sync.mdc) | Read/sync claude-design-docs for UI work |
| [dual-qa-gate skill](./.cursor/skills/dual-qa-gate/SKILL.md) | Gate A + B |
| [agent-verify skill](./.cursor/skills/agent-verify/SKILL.md) | Gate C |
| [ui-product-sync skill](./.cursor/skills/ui-product-sync/SKILL.md) | Sync PRODUCT-SOURCE-OF-TRUTH after UI changes |
| [ADR-001 diagnosis](./docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md) | Business decisions — adaptive interview CTRR |
| [diagnosis-interview](./.cursor/rules/diagnosis-interview.mdc) | Globs diagnosis FE/BE — read ADR + product spec |
| [cv-ingest](./.cursor/rules/cv-ingest.mdc) | PDF CV extract policy |
| [langsmith-inspect](./.cursor/rules/langsmith-inspect.mdc) | LangSmith CLI trace inspection for LLM debugging |
| [langsmith-inspect skill](./.cursor/skills/langsmith-inspect/SKILL.md) | CLI commands, filters, Career Forge graph names |
| [local-debug](./.cursor/rules/local-debug.mdc) | Docker, CORS, API smoke — always on runtime errors |
| [local-debug skill](./.cursor/skills/local-debug/SKILL.md) | Stack ports, log paths, curl recipes, common fixes |

Hackathon history: [docs/archive/](./docs/archive/)

---

## LLM observability

LangSmith traces every `GraphRun`. Before changing prompts, graphs, or streaming:

1. `./scripts/langsmith-env.sh` — confirm `LANGSMITH_PROJECT` and API key (from `.env`, never committed)
2. `./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --last-n-minutes 60 --format pretty`
3. `./scripts/langsmith-env.sh trace get <trace-id> --full --show-hierarchy` for GraphExecutor trees

Full workflow: [langsmith-inspect skill](./.cursor/skills/langsmith-inspect/SKILL.md). CLI install: `curl -fsSL https://cli.langsmith.com/install.sh | sh` → `~/.local/bin/langsmith`.

---

## Commands

| Command | When |
|---------|------|
| `make up` / `make down` / `make status` | Local docker stack |
| `make test` | Backend pytest — before merge |
| `make smoke` | Full harness + stack health |
| `make agent-verify` | Gate C — structure + optional runtime `/health` |
| `./scripts/langsmith-env.sh` | LangSmith env status + CLI version |
| `./scripts/langsmith-env.sh trace list …` | Recent traces (sources `.env` automatically) |

---

## Cursor Cloud / Linear

Full bootstrap: [docs/CURSOR-CLOUD.md](./docs/CURSOR-CLOUD.md).

| Item | Value |
|------|-------|
| Linear workspace | [career-forge-v2](https://linear.app/career-forge-v2) |
| Team key | `CAR` |
| Preferred MCP | Cursor **Linear** plugin (OAuth) |
| Branch format | `CAR-XX-title-slug` (no username prefix) |

Do **not** commit API keys.

---

## Linear branch naming

```
CAR-XX-title-slug
```

Example: `CAR-5-swap-goals-minimal-catalog-seeds-llm-tracks`

Branch name is for **git hygiene only** — status transitions are **manual** (see end-task-workflow).

---

## North star (demo)

> Onboarding → **Live Roadmap Forge (stream)** → skill graph reveal → **Validate with AI** → roadmap reacts.

v2 goals: `rag-engineer` · `agent-engineer` · `llm-evals` · `fine-tuning` — see [V2-PLAN](./docs/V2-PLAN.md).

Design reference: [`claude-design-docs/prototype/README.md`](./claude-design-docs/prototype/README.md)

UI source of truth: [`claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md`](./claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md)
