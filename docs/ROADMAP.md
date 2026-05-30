# ROADMAP — Career Forge

> **Navigation:** [SPRINT-BOARD](./SPRINT-BOARD.md) · [STATUS](./STATUS.md) · [CHECKPOINT](./CHECKPOINT.md) · [Linear project — Career Forge](https://linear.app/hackas-borderless/project/career-forge-soft-push-b0fb1f68c110)

Execution order for hackathon week. **One issue = one branch = one merge.**

Branch format: `HAC-XX-title-slug` (git hygiene). Linear status: **manual** via [end-task-workflow](../.cursor/rules/end-task-workflow.mdc).

**MVP target (Arthur sync):** ~2026-05-29 (quinta) · **Pitch:** 7 min demo ao vivo

Full sprint board: [SPRINT-BOARD.md](./SPRINT-BOARD.md) · Agent lifecycle: [engineering/AGENT-LIFECYCLE.md](./engineering/AGENT-LIFECYCLE.md)

---

## Sprint 0 — Harness & prototype ✅

- [x] **HAC-19** — Engineering lifecycle + agent harness
- [x] **HAC-20** — UI product source of truth docs + sync rule/hook
- [x] **HAC-21** — UX paradigm doc update (editable diagnosis + forge redesign)
- [x] **HAC-22** — Rename product to Career Forge (docs, prototype, harness)
- [x] **HAC-23** — Borderless UI theming guidance (docs, references, prototype CSS Phase 1)
- [x] **HAC-24** — Prototype onboarding pills, minimal goal, vertical graph, 404 fix
- [x] **HAC-25** — Prototype artifact mode: steady trail canvas, node drawer, uniform forge nodes
- [x] **HAC-26** — Backlog compliance audit (docs + Linear HAC-5–18 alignment)
- [x] **HAC-30** — Arthur sync — sprint roadmap + agent lifecycle

---

## Sprint 1 — Foundation **[P] parallel**

**Target:** 2026-05-27 · **Dispatch:** [parallel-dispatch](../.cursor/rules/parallel-dispatch.mdc)

- [x] **HAC-5** [P] — Monorepo Next.js + FastAPI + Postgres + deploy
- [x] **HAC-6** [P] — Skill graph schema + roadmap.json seed
- [x] **HAC-7** [P] — Pydantic + LangGraph state contracts
- [x] **HAC-31** — Professional scaffold (`apps/backend` + `apps/frontend`)
- [x] **HAC-32** — AI execution layer (`GraphRun`, `GraphExecutor`, `AgentFactory`)

**Parallel:** HAC-5, HAC-6, HAC-7 after HAC-19 (no cross-deps)

---

## Sprint 2 — Identity + Forge (core wow)

**Target:** 2026-05-29 (MVP)

- [x] **HAC-8** — Identity Engine (onboarding diagnóstico + **editable diagnosis** screen)
- [x] **HAC-18** — Live Roadmap Forge (LangGraph SSE + animation reveal) ⭐

**Sequential:** HAC-8 → HAC-18

> Forge UI is **timeline-only during stream** (no graph preview). Reveal animates into **vertical roadmap.sh-style layout**. See [UX-FLOW.md](../claude-design-docs/UX-FLOW.md).

---

## Sprint 3 — Artifact UI

**Target:** 2026-05-30

- [x] **HAC-9** — Vertical roadmap UI (steady state + optional AI sidebar)

**Sequential:** HAC-18 → HAC-9

---

## Sprint 4 — Mastery loop

**Target:** 2026-05-31

- [x] **HAC-10** — AI Mastery Validation
- [x] **HAC-11** — Adaptive Planning
- [x] **HAC-12** — Demo mode + seed Ana

**Sequential:** HAC-10 → HAC-11 → HAC-12

---

## Sprint 5 — Stretch P1 **[P] where possible**

**Target:** 2026-06-01

- [x] **HAC-13** [P] — Contextual Mentor
- [x] **HAC-14** [P] — Mock Interview Loop
- [x] **HAC-15** [P] — Relatório mentor

**Parallel:** HAC-13, HAC-14, HAC-15 after HAC-12 (HAC-15 also needs HAC-10)

---

## Sprint 6 — AI diagnosis interview (P0 post-MVP) ⭐

**Authority:** [ADR-001](./decisions/ADR-001-adaptive-diagnosis-ctrr.md) · [DIAGNOSIS-INTERVIEW](./product/DIAGNOSIS-INTERVIEW.md)

**Why:** Hackathon rule — remove AI, app stops. Screen 2 must be LLM-driven (CTRR + Interviewer/Judge).

- [x] **HAC-33** — CV ingest MVP (PDF extract + optional CvSignals) — supports skip logic
- [x] **HAC-42** — Rubric schemas + CTRR contracts
- [x] **HAC-43** — `diagnosis_interview` graph (Judge + Interviewer)
- [x] **HAC-44** — Multi-turn session API + Postgres
- [x] **HAC-45** — Frontend adaptive UI (dumb renderer)
- [x] **HAC-46** — Saturation guardrails + LLM fallback
- [x] **HAC-47** — Onboarding diagnosis polish + observability harness

**Sequential:** HAC-42 → HAC-43 → HAC-44 → HAC-45 → HAC-46 · HAC-33 parallel with HAC-42–44 · HAC-47 post-merge polish

---

## Tech debt cleanup

- [x] **HAC-35** — Consolidate fragmented session stores (`lib/session/storage.ts`)
- [x] **HAC-50** — VPS production deploy hardening (GHCR namespace `pedroalano`, monorepo Dockerfile paths in CI, nginx envsubst safety, curl-based post-deploy health check)
- [x] **HAC-51** — Complete application overview + full documentation sync
- [x] **HAC-59** — Prod skill catalog bootstrap (always seed `skill_nodes` on deploy; `SEED_DEMO_ANA` opt-in for demo Ana)
- [x] **HAC-58** — Prod Postgres persistence stores (`DIAGNOSIS_SESSION_STORE` + `GRAPH_RUN_STORE`)
- [x] **HAC-53** — Diagnosis screen UX (view-first edit, dnd-kit reorder)
- [x] **HAC-52** — Roadmap motor API (`POST /diagnosis/confirm`, forge loads profile, 202 + run_id)
- [x] **HAC-54** — Web search enrichment (OpenAI native `web_search`, live source cards, planner/evaluator StudyPlan loop)
- [x] **HAC-55** — LLM learning graph persistence (dynamic StudyPlan nodes, references/tasks, reload order)
- [x] **HAC-63** — Roadmap drawer progress (check tasks/references, progress bar, `PATCH /roadmap/nodes/{id}/checklist`)
- [x] **HAC-64** — Mock interview + validation for generated StudyPlan nodes (resolve ai-generated context, preserve checklist evidence, recalibrate graph)
- [x] **HAC-65** — Agent-generated MCQ mock interview (LLM A–D + server-side answer key, deterministic scoring, InterviewLoop pills)
- [x] **HAC-57** — Diagnosis confirm → save DB → profile-only `POST /forge` → SSE redirect
- [x] **HAC-66** — Mock interview on-topic (LLM commits to technical subject, forbids study logistics, grounds in references)
- [x] **HAC-67** — Knowledge gap ledger + async classifier (`knowledge_gaps` table, fire-and-forget gap classification, searchable memory)
- [x] **HAC-68** — Close the adaptive loop (mentor reads gaps, next mock weights gaps, drawer "Focos da última tentativa")
- [x] **HAC-69** — Forge re-plan remediation (high-severity gaps inject self-cleaning remediation tasks into the chapter, "Adaptação" badge)
- [x] **HAC-70** — Planner emits `key_concepts` per node (canonical concept source for mock + tutor, persisted via migration 006)
- [x] **HAC-71** — Chapter Q&A tutor (AI grounded in `key_concepts` + references + open gaps via GraphExecutor, `TutorDrawer`)

---

## Backlog / Won't do

| Issue | Title | Status |
|-------|-------|--------|
| HAC-16 | CV from Evidence (P2) | Backlog |
| HAC-17 | Claude Design HTML handoff | Backlog |
| HAC-28 | Gamificação streak + níveis | Cancelled |
| HAC-29 | Auto-posts de progresso | Cancelled |
| HAC-30 | Onboarding horas/dia pacing | Cancelled |

Decisions: [decisions/README.md](./decisions/README.md) · [ADR-001](./decisions/ADR-001-adaptive-diagnosis-ctrr.md) · [2026-05-25 sync Arthur](./decisions/2026-05-25-sync-arthur.md)

---

## Subagent prompt template

```
Repo: HB01-2026_soft-push. Read AGENTS.md → ROADMAP → SPRINT-BOARD → STATUS → CHECKPOINT.
Issue: HAC-XX only. Branch: HAC-XX-slug.
Triple gate before merge. End-task after merge.
If batch is [P]: parent launches parallel Tasks in ONE message.
```

---

## Linear hygiene

- Start issue: `save_issue` state `In Progress`
- Finish issue: **end-task-workflow** → `Done` + STATUS.md + checkbox here
- Milestones: Sprint 1–5 on Linear project

---

*Source of truth for agents — keep in sync with Linear.*
