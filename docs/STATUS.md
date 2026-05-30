# STATUS — Career Forge

> **Navigation:** [ROADMAP](./ROADMAP.md) · [SPRINT-BOARD](./SPRINT-BOARD.md) · [CHECKPOINT](./CHECKPOINT.md) · [AGENTS.md](../AGENTS.md)

Last updated: **2026-05-30** · Last merge: **HAC-70/71** (canonical key_concepts + chapter Q&A tutor — adaptive learning product complete)

---

## Parity matrix

| Area | Status | Notes |
|------|--------|-------|
| Agent harness | ✅ Done | AGENTS.md, rules, hooks, triple gate docs |
| Agent lifecycle + sprint board | ✅ Done | HAC-30 — AGENT-LIFECYCLE, SPRINT-BOARD, parallel-dispatch |
| Professional repo scaffold | ✅ Done | HAC-31 — `apps/backend` + `apps/frontend`, REPO-STRUCTURE.md |
| Claude Design prototype | ⚠️ Partial sync | Artifact mode (HAC-25); pill diagnostic; drift on forge stream |
| UX documentation | ✅ Done | UX-FLOW, SCREEN-INTENT, artifact mode spec |
| Borderless theming (HAC-23) | ✅ Done | BORDERLESS-THEMING, prototype CSS vars, Tailwind tokens in frontend |
| Backlog compliance (HAC-26) | ✅ Done | Docs + Linear HAC-5–18 aligned |
| Linear sprint milestones | ✅ Done | Sprint 1–5 milestones + deps (HAC-30) |
| Monorepo apps/frontend + apps/backend | ✅ Done | HAC-5 + HAC-31 — domain-oriented layers |
| Postgres schema + seed | ✅ Done | HAC-6 — models, Alembic, roadmap.json, seed Ana |
| AI JSON contracts | ✅ Done | HAC-7 — Pydantic schemas + fixtures migrated to `career_forge/schemas/` |
| AI execution layer scaffold | ✅ Done | HAC-32 — `career_forge/ai/`, GraphRun, GraphExecutor, AgentFactory |
| Identity onboarding + editable diagnosis | ✅ Done | HAC-8 — goal picker, pill rounds, POST /diagnosis via GraphExecutor |
| Live Roadmap Forge (timeline-only SSE) | ✅ Done | HAC-18 — forge graph + SSE timeline + reveal |
| Vertical roadmap UI — artifact mode | ✅ Done | HAC-9 — GET /roadmap, vertical spine, node drawer |
| Mastery Validation | ✅ Done | HAC-10 — validation graph, /validate interview UI, score ring |
| Adaptive Planning | ✅ Done | HAC-11 — GraphPatch pós-validação, mission banner, nó revisar destacado |
| Demo mode + seed Ana | ✅ Done | HAC-12 — GET /demo/ana, seed js/git validations, Demo Ana toggle, Docker auto-seed |
| Contextual Mentor | ✅ Done | HAC-13 — mentor agent via GraphExecutor, POST/GET /mentor, drawer + Ask AI |
| Mock Interview Loop | ✅ Done | HAC-14 — 5–7 contextual Qs, mock_interview graph, trail recalibration |
| Mentor report | ✅ Done | HAC-15 — GET /mentor-report, /report artifact page, evidence + interventions |
| Frontend session storage | ✅ Done | HAC-35 — shared `lib/session/storage.ts`, domain modules preserved |
| CTRR diagnosis interview schemas | ✅ Done | HAC-42 — `diagnosis_interview.py` contracts + frontend `contracts.ts` sync |
| CV ingest (PDF + CvSignals) | ✅ Done | HAC-33 — `services/cv.py`, optional Screen 1 attach |
| Adaptive diagnosis interview graph | ✅ Done | HAC-43 — `diagnosis_interview` Judge + Interviewer via GraphExecutor |
| Diagnosis session API + Postgres | ✅ Done | HAC-44 — `POST /diagnosis/interview/start|turn`, `diagnosis_sessions` table |
| Frontend adaptive diagnosis UI | ✅ Done | HAC-45 — DiagnosticPills uses interview API, sidebar from `mapping_progress` |
| Diagnosis guardrails | ✅ Done | HAC-46 — max 5 rounds, LLM 503 retry, agent-verify checks |
| Diagnosis polish + observability | ✅ Done | HAC-47 — fail-fast LLM, CORS 3300, LangSmith/local-debug harness, UX refactor, dead code cleanup |
| VPS deploy pipeline hardening | ✅ Done | GHCR namespace `ghcr.io/pedroalano`, monorepo Dockerfile build paths fixed, SSH deploy health check migrated from Python to `curl` |
| Prod skill catalog seed on deploy | ✅ Done | HAC-59 — prod/dev entrypoints always run `scripts.seed`; `SEED_DEMO_ANA` only for demo Ana; `data/roadmap.json` documented in DEPLOY-VPS |
| Prod Postgres persistence stores | ✅ Done | HAC-58 — `DIAGNOSIS_SESSION_STORE` + `GRAPH_RUN_STORE` → Postgres when `ENV=production` |
| Diagnosis screen UX (view-first edit) | ✅ Done | HAC-53 — inline edit icons, add/delete, dnd-kit priority reorder, refazer diagnóstico |
| Diagnosis confirm + forge motor API | ✅ Done | HAC-52 — `POST /diagnosis/confirm`, `POST /forge` loads profile (202 + run_id) |
| Forge web search + StudyPlan loop | ✅ Done | HAC-54 — OpenAI native `web_search`, progressive source cards, planner/evaluator loop, `graph_ready` from approved StudyPlan |
| Generated roadmap persistence + references | ✅ Done | HAC-55 — approved StudyPlan persists as dynamic roadmap nodes with tasks, references, prerequisites, and stable ordering |
| Roadmap drawer checklist progress | ✅ Done | HAC-63 — task/reference checkboxes, study progress bar, `PATCH /roadmap/nodes/{id}/checklist`, compact bar on canvas cards |
| Mock interview on generated StudyPlan nodes | ✅ Done | HAC-64 — `/mock-interview` + `/validation/questions` resolve ai-generated nodes; evidence/tasks preserved through recalibration |
| MCQ mock interview (agent-generated) | ✅ Done | HAC-65 — LLM MCQ A–D + server-side answer key; deterministic score on submit; InterviewLoop mode=loop pills |
| Diagnosis confirm → forge motor (FE wire) | ✅ Done | HAC-57 — confirm saves profile; `POST /forge` profile-only; `/forge` SSE from stored run_id |
| Mock interview on-topic | ✅ Done | HAC-66 — generator commits to technical subject, forbids study-logistics questions, grounds in references; per-question concept |
| Knowledge gap ledger (adaptive memory) | ✅ Done | HAC-67 — `knowledge_gaps` table; async fire-and-forget classifier (concept/severity/remediation); ON CONFLICT upsert; correct answers resolve gaps |
| Adaptive loop closed | ✅ Done | HAC-68 — mentor reads concept-level gaps, next mock targets open gaps (gap_probe), node drawer shows "Focos da última tentativa", `GET /knowledge-gaps` |
| Chapter reacts to gaps (remediation) | ✅ Done | HAC-69 — open high-severity gaps inject self-cleaning remediation tasks into the node (stable id, resolved-aware); drawer "Adaptação" badge |
| Canonical key_concepts per node | ✅ Done | HAC-70 — planner emits 3-6 atomic technical concepts/node; persisted (migration 006); shared source for mock + tutor |
| Chapter Q&A tutor (AI) | ✅ Done | HAC-71 — `tutor` agent via GraphExecutor grounded in key_concepts + references + open gaps; `GET /tutor/context` + `POST /tutor`; `TutorDrawer` from node drawer |

---

## Current sprint

**Sprint 7 — Sync 2026-05-26 production push** — ✅ complete

| Issue | Title | State |
|-------|-------|-------|
| **HAC-58** | Prod Postgres stores | **Done** |
| **HAC-53** | Diagnosis screen UX | **Done** |
| **HAC-52** | Roadmap motor API — persist + forge | **Done** |
| **HAC-54** | Web search enrichment — live study sources | **Done** |
| **HAC-55** | LLM graph persistence + references | **Done** |
| **HAC-57** | Diagnosis confirm → save → forge (Arthur) | **Done** |
| **HAC-66** | Mock interview on-topic (technical subject) | **Done** |
| **HAC-67** | Knowledge gap ledger + async classifier | **Done** |
| **HAC-68** | Close adaptive loop (mentor/mock/drawer) | **Done** |
| **HAC-63** | Roadmap drawer progress (checklist + `PATCH /roadmap/nodes/{id}/checklist`) | **Done** |
| **HAC-64** | Mock interview + validation on generated StudyPlan nodes | **Done** |
| **HAC-65** | Agent-generated MCQ mock interview with answer-key scoring | **Done** |
| **HAC-69** | Forge re-plan remediation (gaps → chapter tasks) | **Done** |
| **HAC-70** | Planner emits key_concepts per node | **Done** |
| **HAC-71** | Chapter Q&A tutor (AI grounded) | **Done** |

**Sprint 7 complete** — all issues merged. Adaptive learning loop + chapter tutor shipped (HAC-66→71).

### Previous ops batch

**Sprint 6 — AI diagnosis interview (P0)** ✅

| Issue | Title | Class | State |
|-------|-------|-------|-------|
| **HAC-33** | CV ingest MVP | — | **Done** |
| **HAC-42** | CTRR schemas | — | **Done** |
| **HAC-43** | diagnosis_interview graph | S | **Done** |
| **HAC-44** | Session API + Postgres | S | **Done** |
| **HAC-45** | Frontend adaptive UI | S | **Done** |
| **HAC-46** | Guardrails + fallback | S | **Done** |
| **HAC-47** | Polish + observability harness | S | **Done** |

Sprint 6 complete — adaptive diagnosis interview live on onboarding path ([DIAGNOSIS-INTERVIEW](./product/DIAGNOSIS-INTERVIEW.md)). HAC-47 adds fail-fast LLM, local-debug/LangSmith harness, and UX polish.

---

## Arthur sync decisions (2026-05-25)

| Decision | Status |
|----------|--------|
| MVP funcional ~quinta 2026-05-29 | ✅ Milestones set |
| Pitch 7 min demo ao vivo | ✅ HAC-12 scoped |
| Arthur → frontend TS; backend FastAPI | ✅ HAC-5 updated |
| Parallel Sprint 1 (HAC-5/6/7) | ✅ Labels + rule |
| Won't-do: gamificação, auto-posts, horas/dia | ✅ HAC-27–29 Cancelled |

Full doc: [decisions/2026-05-25-sync-arthur.md](./decisions/2026-05-25-sync-arthur.md)

---

## Demo readiness

| Scene | Ready |
|-------|-------|
| UI prototype (artifact mode + onboarding pills) | ⚠️ |
| Onboarding flow wired to API | ✅ |
| Adaptive diagnosis interview (CTRR) | ✅ |
| UX docs + steady-state reference | ✅ |
| Sprint board + agent lifecycle | ✅ |
| Professional monorepo scaffold | ✅ |
| Live forge SSE (timeline-only) | ✅ |
| Vertical roadmap steady state | ✅ |
| Mastery validation interview | ✅ |
| Mock interview loop (5–7 Qs) | ✅ |
| End-to-end pitch | ✅ |
| Contextual mentor chat | ✅ |
| Mentor report (Borderless) | ✅ |

---

## Blockers

- Confirmação formal participação Arthur (pendente da call)

---

*Update this file after every merge (end-task workflow).*
