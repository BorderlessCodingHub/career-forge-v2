# ADR-001: Adaptive diagnosis interview (CTRR)

| Field | Value |
|-------|-------|
| **Status** | Superseded (dimensions) — see [ADR-002](./ADR-002-universal-profile-framework.md) |
| **Date** | 2026-05-25 |
| **Deciders** | Career Forge team (hackathon) |
| **Linear** | HAC-42 … HAC-46 · parent context HAC-33 (CV) |

---

## Context

### Hackathon rule (non-negotiable)

> If you remove AI, the project stops working. AI is the engine, not a sticker.

Screen 2 (onboarding diagnosis) **must** be LLM-driven. The current rule-based `build_diagnosis_response()` and static `DIAG_ROUNDS` in the frontend violate this for the production path.

### Audience

**Career transition to tech** — often from zero or early study. We do **not** optimize for senior hiring signals (enterprise scale, staff-level ownership). Dimensions are reframed for **readiness**, not **hireability**.

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
| `learning_stage` | Senioridade | Dreyfus-lite: novice / advanced beginner — not "senior backend" |
| `project_scope` | Escala | Largest thing built (todo app, API, deploy) — not distributed systems |
| `background_context` | Contexto | Prior domain + learning style (bootcamp vs self-study) |
| `hands_on_evidence` | Experiência prática | STAR-lite: something built or attempted |
| `git` | Git | aware vs practiced |
| `client_server` | Cliente/servidor | mental model |
| `http_apis` | HTTP & APIs | exposure |
| `database` | Banco de dados | exposure |

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

| Now (HAC-33b + interview) | Later |
|----------------------------|-------|
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

- Meets hackathon AI-first requirement on identity engine
- Sidebar "O que a IA está mapeando" reflects real `belief_state`
- Auditable transcript + belief for demo / mentors

### Negative / tradeoffs

- Requires LLM API key + latency budget per turn
- More moving parts than keyword scoring — needs guardrails (HAC-46)

### Supersedes

- Static `DIAG_ROUNDS` + keyword `DOMAIN_SIGNALS` as **production** diagnosis path
- HAC-8 rule-only graph for user-facing onboarding (kept as fallback/dev)

---

## Implementation map

| Linear | Scope |
|--------|-------|
| HAC-33 | CV epic — update scope per this ADR |
| HAC-42 | Rubric schemas + Pydantic contracts |
| HAC-43 | `diagnosis_interview` graph (Judge + Interviewer) |
| HAC-44 | Multi-turn session API + Postgres |
| HAC-45 | Frontend adaptive UI (replace static pills data) |
| HAC-46 | Saturation, max rounds, LLM failure fallback |

**Spec:** [docs/product/DIAGNOSIS-INTERVIEW.md](../product/DIAGNOSIS-INTERVIEW.md)

**Cursor rule:** `.cursor/rules/diagnosis-interview.mdc`
