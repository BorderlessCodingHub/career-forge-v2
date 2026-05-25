# Career Forge — Agent harness (index)

**Career Forge** (Soft Push) — AI-native learning system: skill graph adaptativo, Live Roadmap Forge com streaming, validação de mastery por IA.

**Stack:** Next.js (web) · FastAPI (api) · PostgreSQL · LangGraph + LangChain + LangSmith

This file is the **table of contents**. Details live under [`docs/`](./docs/README.md) and [`claude-design-docs/`](./claude-design-docs/README.md).

---

## Start here — by task type

| Task | Read in order | Then do |
|------|---------------|---------|
| **Implement a Linear issue** | [ROADMAP](./docs/ROADMAP.md) → [SPRINT-BOARD](./docs/SPRINT-BOARD.md) → [STATUS](./docs/STATUS.md) → [CHECKPOINT](./docs/CHECKPOINT.md) → issue scope → [AGENT-DELIVERY](./docs/AGENT-DELIVERY.md) | Worktree `../worktrees/hac-XX-<slug>` · branch `HAC-XX-title-slug` · triple gate · merge · **end-task** |
| **AI / LangGraph work** | [EXECUTION-FLOW](./docs/engineering/EXECUTION-FLOW.md) → [AI-EXECUTION](./docs/engineering/AI-EXECUTION.md) → [REPO-STRUCTURE](./docs/engineering/REPO-STRUCTURE.md) § AI layer | Use `GraphExecutor` + `AgentFactory` — no per-graph streaming |
| **Debug LLM / traces** | [langsmith-inspect skill](./.cursor/skills/langsmith-inspect/SKILL.md) → [langsmith-inspect rule](./.cursor/rules/langsmith-inspect.mdc) | `./scripts/langsmith-env.sh` loads `.env` · inspect traces before changing prompts/graphs |
| **Local runtime / failed to fetch** | [local-debug skill](./.cursor/skills/local-debug/SKILL.md) → [local-debug rule](./.cursor/rules/local-debug.mdc) | Docker logs · CORS · `logs/backend.log` when `ENV=local` |
| **Diagnosis / onboarding AI** | [ADR-001](./docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md) → [DIAGNOSIS-INTERVIEW](./docs/product/DIAGNOSIS-INTERVIEW.md) → [diagnosis-interview rule](./.cursor/rules/diagnosis-interview.mdc) | Multi-turn CTRR · ≤2 Q/turn · FE dumb renderer · HAC-42–46 |
| **Bootstrap / first session** | [ROADMAP](./docs/ROADMAP.md) → [SPRINT-BOARD](./docs/SPRINT-BOARD.md) → [STATUS](./docs/STATUS.md) → [CHECKPOINT](./docs/CHECKPOINT.md) | Paste block below · `make smoke` when apps exist |
| **Cloud agent / Linear MCP** | [CURSOR-CLOUD](./docs/CURSOR-CLOUD.md) | Set `HACKATON_LINEAR_API_KEY` in [Cloud secrets](https://cursor.com/dashboard/cloud-agents) · repo [`.cursor/mcp.json`](./.cursor/mcp.json) |
| **Agent lifecycle / sprint planning** | [AGENT-LIFECYCLE](./docs/engineering/AGENT-LIFECYCLE.md) → [SPRINT-BOARD](./docs/SPRINT-BOARD.md) | Classify P/S/B · parallel dispatch for [P] batches |
| **UI from Claude Design** | [PRODUCT-SOURCE-OF-TRUTH](./claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md) → [claude-design-docs/README.md](./claude-design-docs/README.md) | Map prototype → Next.js; sync docs after paradigm change |
| **Delivery / merge** | [AGENT-DELIVERY](./docs/AGENT-DELIVERY.md) → [end-task-workflow](./.cursor/rules/end-task-workflow.mdc) | `SHIP + PASS + VERIFIED` then **manual Done in Linear** |

---

## Nova sessão — bootstrap manual

Paste as first agent message if hooks unavailable:

```
Repo: HB01-2026_soft-push (Career Forge hackathon).
Read AGENTS.md → ROADMAP → SPRINT-BOARD → STATUS → CHECKPOINT → EXECUTION-FLOW (AI work).
Pick current ROADMAP batch only. Branch: HAC-XX-title-slug.
Before merge: triple gate (docs/AGENT-DELIVERY.md). make test && make smoke when runtime touched.
After merge: end-task — manually set Linear issue to Done (no GitHub↔Linear automation).
Update docs/STATUS.md + ROADMAP checkboxes.
```

---

## Subagent Task template (mandatory for parent)

```
Repo: HB01-2026_soft-push. Base: origin/main (pull latest).

Read AGENTS.md → docs/ROADMAP.md → docs/STATUS.md → docs/CHECKPOINT.md before coding.
Scope: single issue HAC-XX only.

Branch: HAC-XX-title-slug
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
  → ROADMAP.md           current sprint, deps
  → SPRINT-BOARD.md      [P] parallel groups, milestones
  → STATUS.md            parity matrix, last merge
  → CHECKPOINT.md        product, stack, wow features
  → issue scope          Linear MCP
  → claude-design-docs/  UI intent (when front-end)
      PRODUCT-SOURCE-OF-TRUTH.md first
  → AGENT-DELIVERY.md    triple QA gate
  → end-task-workflow    manual Linear Done
```

Full lifecycle: [docs/engineering/AGENT-LIFECYCLE.md](./docs/engineering/AGENT-LIFECYCLE.md)

---

## Rules & skills

| Resource | Purpose |
|----------|---------|
| [EXECUTION-FLOW](./docs/engineering/EXECUTION-FLOW.md) | E2E tree, parallel dispatch, Postgres checkpointer |
| [AI-EXECUTION](./docs/engineering/AI-EXECUTION.md) | GraphRun, GraphExecutor, AgentFactory, stream vs collect |
| [ai-execution](./.cursor/rules/ai-execution.mdc) | GraphExecutor-only path for AI/LangGraph changes |
| [AGENT-LIFECYCLE](./docs/engineering/AGENT-LIFECYCLE.md) | Session entry → planning → impl → QA → exit |
| [SPRINT-BOARD](./docs/SPRINT-BOARD.md) | Sprint goals, [P] groups, fit/no-fit table |
| [CURSOR-CLOUD](./docs/CURSOR-CLOUD.md) | Cloud bootstrap · Linear HTTP MCP · `HACKATON_LINEAR_API_KEY` |
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

## Cursor Cloud specific instructions

Cloud agents clone this repo only. Full bootstrap: [docs/CURSOR-CLOUD.md](./docs/CURSOR-CLOUD.md).

| Item | Value |
|------|-------|
| Linear MCP config | [`.cursor/mcp.json`](./.cursor/mcp.json) — HTTP Bearer via `HACKATON_LINEAR_API_KEY` |
| Secret name | `HACKATON_LINEAR_API_KEY` |
| Dashboard | [cursor.com/dashboard/cloud-agents](https://cursor.com/dashboard/cloud-agents) → **Secrets** tab |
| Linear key source | Linear → Settings → API → Personal API keys (hackas-borderless workspace) |

Do **not** commit API keys. Restart Cloud agents after adding or rotating secrets.

---

## Linear branch naming

```
HAC-XX-title-slug
```

Example: `HAC-18-live-roadmap-forge-langgraph-streaming`

Use Linear **Copy git branch name** when available. Branch name is for **git hygiene only** — status transitions are **manual** (see end-task-workflow).

---

## North star (demo)

> Onboarding → **Live Roadmap Forge (stream)** → skill graph reveal → **Validar com IA** → trilha reage.

Design reference: [`claude-design-docs/prototype/README.md`](./claude-design-docs/prototype/README.md) — `http://localhost:8765/`

UI source of truth: [`claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md`](./claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md)
