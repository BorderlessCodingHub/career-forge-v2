# ADR-001: Adaptive diagnosis interview (CTRR)

| Field | Value |
|-------|-------|
| **Status** | **Binding in v2** for Judge/Interviewer loop + CTRR 4 dims (Conceptual / Technical / Readiness / Resourcefulness). Dimension sprawl notes in ADR-002 are historical; v2 F2 keeps CTRR per [V2-PLAN.md](../V2-PLAN.md). |
| **Date** | 2026-05-25 · v2 note 2026-07-21 |
| **Deciders** | Career Forge team |
| **Linear (v2)** | Prompt recalibration + soft gate in Phase 2 |

---

## Context

### AI-first rule (non-negotiable)

> If you remove AI, the project stops working. AI is the engine, not a sticker.

Screen 2 (onboarding diagnosis) **must** be LLM-driven. Rule-based `build_diagnosis_response()` and static `DIAG_ROUNDS` in the frontend violate this for the production path.

### Audience

**v2:** BASE and PSP learners only — spectrum from early career (~6 months XP) to decades of experience. Optimize for readiness toward **LLM engineer** tracks, not enterprise staff hiring.

### Screen 1 inputs

- Goal, motivation, years of XP (self-reported)
- Optional CV attach (**PDF-only** for MVP ingest)

---

## Decision

### 1. Framework: CTRR + Rubric Saturation Loop

**CTRR** = Career Transition Readiness Rubric.

Two LLM roles (see [Rubric-Aware Interview](https://arxiv.org/html/2603.01775)):

| Role | Responsibility |
|------|----------------|
| **Judge** | Maintains `belief_state` per rubric dimension (confidence 0–1 + evidence snippets) |
| **Interviewer** | Generates **at most 2 questions** per turn for dimensions below saturation threshold |

**Saturation:** all dimensions ≥ `0.75` confidence **OR** max **5 rounds** (10 questions) → finalize `DiagnosisResponse`.

### 2. Rubric dimensions (v1)

| Key | UI label (sidebar) | Measures |
|-----|-------------------|----------|
| `learning_stage` | Seniority | Dreyfus-lite: novice / advanced beginner — not "senior backend" |
| `project_scope` | Scale | Largest thing built (todo app, API, deploy) — not distributed systems |
| `background_context` | Context | Prior domain + learning style (bootcamp vs self-study) |
| `hands_on_evidence` | Hands-on experience | STAR-lite: something built or attempted |
| `git` | Git | aware vs practiced |
| `client_server` | Client/server | mental model |
| `http_apis` | HTTP & APIs | exposure |
| `database` | Database | exposure |

Skip dimensions already evidenced in intake, CV extract, or prior turns.

### 3. Question contract (Interviewer output)

```json
{
  "topic": "Senioridade",
  "rubric_key": "learning_stage",
  "question": "…",
  "example_of_answer": "…"
}
```

Frontend is a **dumb renderer** — no hardcoded rounds in production.

### 4. CV policy

| Now (CV + interview) | Later |
|----------------------|-------|
| PDF-only upload | DOCX, LinkedIn |
| Text extract (no LLM) | — |
| Optional LLM `CvSignals` struct once | Full résumé scoring |
| CV **optional** — flow works without file | — |

CV **initializes** Judge belief; never blocks onboarding.

### 5. Execution architecture

- Multi-turn session in **Postgres** (`diagnosis_sessions` + `graph_runs`)
- **`GraphExecutor` + `AgentFactory`** — graph name `diagnosis_interview`
- API: `POST /diagnosis/interview/start`, `POST /diagnosis/interview/{id}/turn`
- Rule-based `POST /diagnosis` one-shot may remain for tests/dev only — **not** production onboarding path

### 6. Single-user product

No Demo Ana toggle on onboarding UI. One anonymous user per browser session.

---

## Consequences

### Positive

- Meets AI-first requirement on identity engine
- Sidebar "What the AI is mapping" reflects real `belief_state`
- Auditable transcript + belief for demo / mentors

### Negative / tradeoffs

- Requires LLM API key + latency budget per turn
- More moving parts than keyword scoring — needs guardrails (max rounds, LLM failure handling)

### Supersedes

- Static `DIAG_ROUNDS` + keyword `DOMAIN_SIGNALS` as **production** diagnosis path
- Rule-only graph for user-facing onboarding (kept as fallback/dev)

---

## Implementation map

Shipped. v2 recalibration: [V2-PLAN.md](../V2-PLAN.md) Phase 2.

| Area | Scope |
|------|-------|
| CV | PDF ingest + optional CvSignals |
| Schemas | Rubric + Pydantic contracts |
| Graph | `diagnosis_interview` (Judge + Interviewer) |
| API | Multi-turn session + Postgres |
| Frontend | Adaptive UI (API-driven questions) |
| Guardrails | Saturation, max rounds, LLM failure fallback |

**Spec:** [docs/product/DIAGNOSIS-INTERVIEW.md](../product/DIAGNOSIS-INTERVIEW.md)

**Cursor rule:** `.cursor/rules/diagnosis-interview.mdc`
