# ADR-002: Universal profile framework (supersedes CTRR scope)

| Field | Value |
|-------|-------|
| **Status** | **Not active in v2 F2.** Historical proposal. v2 keeps CTRR 4 dims + soft gate per [V2-PLAN.md](../V2-PLAN.md). Revisit only via a new ADR. |
| **Date** | 2026-05-25 · annotated 2026-07-21 |
| **Deciders** | Career Forge team (hackathon-era) |
| **Supersedes (partial, historical)** | [ADR-001](./ADR-001-adaptive-diagnosis-ctrr.md) — dimension model only; Judge/Interviewer loop remains in ADR-001 |

> **v2 agents:** follow ADR-001 + [DIAGNOSIS-INTERVIEW.md](../product/DIAGNOSIS-INTERVIEW.md). Do not implement the 5-dimension universal profile from this ADR unless product explicitly reopens it.

---

## Context

### Problem with 8-dimension CTRR (historical)

ADR-001 defined **CTRR** — eight rubric dimensions tuned for backend transition (`git`, `http_apis`, `database`, …). In production testing:

1. **Low mapping velocity** — one interview round often maps only one sidebar dimension (e.g. Context), even when answers mention projects, tools, and learning path.
2. **Role-specific sprawl** — a credible framework for data engineer, fullstack, and AI engineer implies **3× rubric maintenance** (prompts, labels, finalize mapping, sidebar).
3. **Interrogation feel** — up to 5 rounds × 2 questions = 10 turns to saturate 8 dimensions; users compare this to form spam (Gupy-style) and churn before the roadmap.
4. **Goal as framework fork** — `GoalPicker` historically locked non-backend paths (“Coming soon”), forcing backend-shaped questions for everyone.

The AI-first constraint from ADR-001 **still holds**: diagnosis must remain LLM-driven (Judge + Interviewer). This ADR changes **what** is measured, not **whether** AI runs.

### Research synthesis

| Source | Takeaway for Career Forge |
|--------|---------------------------|
| **O*NET Interest Profiler (Mini-IP)** | Fixed **30-question** whole-person instrument; not adaptive, but shows government-grade acceptance of **short** assessments when dimensions are orthogonal and labels are plain language. |
| **O*NET Transferable Skills** | Skills are **occupation-linked ratings**, not a separate quiz — goal (target role) should **filter/prioritize** a universal skill set, not define a new rubric per role. |
| **Dreyfus (simplified)** | Five stages collapse to **three for transition**: *novice*, *advanced beginner*, *competent-in-one-project* — enough for roadmap placement without senior hiring semantics. |
| **Duolingo placement** | **Adaptive CAT**: each answer updates belief; next item maximizes information; **~5–10 min** cap; partial credit on messy answers; unlock/skips derived from estimate — not exhaustive checklist. |
| **LinkedIn / coach pattern** | Intake (goal + story) + **1–2 proof questions** + optional CV; progress shown as “building your profile” not “8/8 skills checked”. |

**Design principle:** one universal belief state; **goal_id** and **CV** are priors; each turn extracts maximum evidence across dimensions.

---

## Decision

### 1. Replace 8 CTRR dimensions with 5 universal dimensions

Role-agnostic keys — backend/data/frontend/AI differ only in **downstream mapping**, not in interview structure.

| Key | UI label | Measures | Typical evidence |
|-----|----------|----------|------------------|
| `motivation_goal` | Goal | Why this path + alignment with stated goal | Screen 1 motivation, goal-specific follow-up |
| `background_transfer` | Where you come from | Prior domain + transferable habits (communication, analysis, ops) | Intake, CV roles, “how you study today” |
| `learning_velocity` | Learning pace | Dreyfus-lite stage + time invested + consistency | years_xp, courses, frequency, recency |
| `hands_on_proof` | Hands-on proof | Largest built/attempted artifact (STAR-lite) | Project story, repo, deploy attempt |
| `constraints` | Real context | Time/week, language, budget, bootcamp vs self-study | Single direct question if not in intake |

**Saturation:** confidence ≥ **0.75** per dimension **OR** **3 interview rounds** (max **6 questions** total) → finalize.

**Removed as first-class dimensions:** per-skill checklist (`git`, `http_apis`, `database`, …). Those become **derived gaps** in `DiagnosisResponse.starting_priorities` based on `(goal_id, hands_on_proof, learning_velocity)` — not separate interview slots.

### 2. Mapping rules (Judge)

```
intake (goal, motivation, years_xp, cv)
  → seed all 5 dimensions (partial confidence)

each answer
  → update EVERY dimension with explicit evidence (multi-label)
  → do NOT restrict updates to question.rubric_key

goal_id
  → parameter in finalize step only:
      track_id, persona_slug, starting_priorities weights
```

**Example:** Answer: *“I built a REST API on GitHub, I use basic Git, 6h/week”*  
→ `hands_on_proof` mapped, `learning_velocity` mapped, `background_transfer` partial; **do not** ask separate git/http/database questions unless `hands_on_proof` still < 0.75 after one clarifier.

### 3. Interviewer rules

- **Max 2 questions per round**, **max 3 rounds** (6 questions hard cap).
- Round 1 must be **open** (“Tell us what you have already done or tried…”) when intake + CV leave ≥3 dimensions unsaturated — avoids pill fatigue.
- Prefer **compound questions** over dimension-per-turn.
- Skip dimensions already ≥ 0.75 from intake/CV/answers.
- `goal_id` may **word** examples (“API” vs “pipeline”) but **same rubric keys**.

### 4. UX principles (anti-spam)

| Rule | Implementation |
|------|----------------|
| **Hard cap** | 3 rounds / 6 questions; then finalize with best-effort belief |
| **Progress ≠ checklist** | Sidebar: “Profile: 60% complete” + 5 dimension chips (not 8 tech silos) |
| **Stop early** | All 5 saturated OR user gives rich round-1 answer mapping ≥4 dims |
| **No dead ends** | Submit always advances or completes; loading state always clears (`finally`) |
| **Goal unlocked day 1** | All `CAREER_GOALS` active; finalize uses `goal_id` parameter |

Copy: *“No right or wrong — the more concrete, the fewer questions.”*

### 5. What stays from ADR-001

- Postgres session + `GraphExecutor` + `diagnosis_interview` graph
- Judge / Interviewer split
- CV optional PDF extract
- Frontend dumb renderer (`InterviewQuestion[]` from API)
- `DiagnosisResponse` contract (profile, strengths, gaps, priorities, mastery)

---

## Consequences

### Positive

- Fewer turns to usable roadmap; lower churn risk
- One prompt/schema path for all career goals
- Rich answers improve mapping in **one shot** (aligns with Judge multi-dimension rule added interim)
- Demo story: “tell us your story → 2 smart follow-ups → roadmap”

### Negative / tradeoffs

- Less granular per-skill telemetry for mentor (mitigate in finalize LLM + roadmap node rationale)
- Requires migration: schema keys, sidebar, prompts, tests, `ctrr-dimensions.ts`
- Hackathon **this week**: full migration is ~1–2 days; risk if attempted alongside forge/validation

---

## Recommendation: implement now vs next sprint

| Item | When | Rationale |
|------|------|-----------|
| Unlock all goals in `GoalPicker` | **Now** ✅ | Trivial; product expectation |
| Fix turn submit + Postgres session store | **Now** ✅ | Bug + data loss on reload |
| Judge multi-dimension from rich answers | **Now** ✅ | Prompt-only; improves current CTRR |
| ADR-002 accepted | **Now** ✅ | Align team before rewrite |
| Replace 8 CTRR keys with 5 universal | **Next sprint** | Touches schemas, FE sidebar, graph, tests, finalize |
| Reduce max rounds 5→3 | **Next sprint** | With universal dims; optional quick config change now |
| Open question round 1 | **Next sprint** | Interviewer prompt + UX copy |
| Derived skill gaps (git/http/db) in finalize | **Next sprint** | Depends on new belief shape |

**Honest hackathon scope:** ship **bugfix + goal unlock + Judge tuning + ADR** now; schedule **schema/prompt migration** immediately after demo if interview still feels long.

---

## Implementation map (when executing migration)

| Area | Change |
|------|--------|
| `schemas/diagnosis_interview.py` | 5 keys, new labels/descriptions, `MAX_INTERVIEW_ROUNDS = 3` |
| `prompts/diagnosis_interview.py` | Universal Judge/Interviewer + goal-aware finalize |
| `apps/frontend/.../ctrr-dimensions.ts` | Rename to `profile-dimensions.ts` (5 items) |
| `finalize_diagnosis` | Map belief + `goal_id` → track + skill gaps |
| Tests | Update mocks + API integration |
| ADR-001 | Add “Superseded by ADR-002” banner on dimension table |

---

## Agent workflow

1. Read ADR-002 before changing rubric keys or interview caps
2. Do **not** add role-specific rubrics without updating this ADR
3. Keep `goal_id` as finalize parameter — never fork Interviewer by role
