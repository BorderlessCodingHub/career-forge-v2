# Career OS — Agent harness (index)

**Career OS** (Soft Push) — AI-native learning system: skill graph adaptativo, Live Roadmap Forge com streaming, validação de mastery por IA.

**Stack:** Next.js (web) · FastAPI (api) · PostgreSQL · LangGraph + LangChain + LangSmith

This file is the **table of contents**. Details live under [`docs/`](./docs/README.md) and [`claude-design-docs/`](./claude-design-docs/README.md).

---

## Start here — by task type

| Task | Read in order | Then do |
|------|---------------|---------|
| **Implement a Linear issue** | [ROADMAP](./docs/ROADMAP.md) → [STATUS](./docs/STATUS.md) → [CHECKPOINT](./docs/CHECKPOINT.md) → issue scope → [AGENT-DELIVERY](./docs/AGENT-DELIVERY.md) | Branch `HAC-XX-title-slug` · implement · triple gate · merge · **end-task** |
| **Bootstrap / first session** | [ROADMAP](./docs/ROADMAP.md) → [STATUS](./docs/STATUS.md) → [CHECKPOINT](./docs/CHECKPOINT.md) | `make smoke` when apps exist |
| **UI from Claude Design** | [claude-design-docs/README.md](./claude-design-docs/README.md) | Map prototype → Next.js components |
| **Delivery / merge** | [AGENT-DELIVERY](./docs/AGENT-DELIVERY.md) → [end-task-workflow](./.cursor/rules/end-task-workflow.mdc) | `SHIP + PASS + VERIFIED` then **manual Done in Linear** |

---

## Nova sessão — bootstrap manual

Paste as first agent message if hooks unavailable:

```
Repo: HB01-2026_soft-push (Career OS hackathon).
Read AGENTS.md → docs/ROADMAP.md → docs/STATUS.md → docs/CHECKPOINT.md.
Pick current ROADMAP batch only. Branch: HAC-XX-title-slug.
Before merge: triple gate (docs/AGENT-DELIVERY.md).
After merge: end-task rule — manually set Linear issue to Done (no GitHub↔Linear automation).
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
AGENTS.md
  → ROADMAP.md           current batch, deps
  → STATUS.md            parity matrix, last merge
  → CHECKPOINT.md        product, stack, wow features
  → issue scope          Linear MCP
  → claude-design-docs/  UI intent (when front-end)
  → AGENT-DELIVERY.md    triple QA gate
  → end-task-workflow    manual Linear Done
```

---

## Rules & skills

| Resource | Purpose |
|----------|---------|
| [linear-delivery-workflow](./.cursor/rules/linear-delivery-workflow.mdc) | Branch, micro-PR, parallel planning |
| [end-task-workflow](./.cursor/rules/end-task-workflow.mdc) | **Manual Linear Done** (no GitHub integration) |
| [dual-qa-gate](./.cursor/rules/dual-qa-gate.mdc) | Triple gate summary |
| [agent-delivery-gate](./.cursor/rules/agent-delivery-gate.mdc) | SHIP + PASS + VERIFIED |
| [end-session-smoke](./.cursor/rules/end-session-smoke.mdc) | `make smoke` before ending session |
| [dual-qa-gate skill](./.cursor/skills/dual-qa-gate/SKILL.md) | Gate A + B |
| [agent-verify skill](./.cursor/skills/agent-verify/SKILL.md) | Gate C |

---

## Commands

| Command | When |
|---------|------|
| `make smoke` | After web/api/infra changes (stub until stack exists) |
| `make agent-verify` | Gate C — API + DB E2E |
| `pnpm test` / `pytest` | Before merge (when configured) |

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

Design reference: [`claude-design-docs/prototype/Career OS.html`](./claude-design-docs/prototype/Career%20OS.html)
