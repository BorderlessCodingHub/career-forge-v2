# CAR-14 — What we built (step by step)

> **Issue:** [CAR-14](https://linear.app/career-forge-v2/issue/CAR-14) — CTRR prompt/rubric recalibration (4 LLM goals) + light validation align  
> **Merged:** 2026-08-02 · PR #17 · `4a6083f` / merge `816bbb4`  
> **Phase:** F2 — Goals LLM + prompts + english-first  
> **Grill:** 2026-08-02 (execution plan locked before coding)

This note explains **what changed and why**, in delivery order — not a line-by-line code tour.

---

## 1. Context — why CAR-14 existed

Phase 2 needs diagnosis + validation that fit **BASE/PSP** learners on four LLM tracks:

- `rag-engineer`
- `agent-engineer`
- `llm-evals`
- `fine-tuning`

Before CAR-14:

- Interviewer / Judge / Finalize prompts were still **Portuguese** and beginner/SWE-flavored (`git` / `http` / `db` gaps).
- Validation keyword banks only covered legacy nodes (`js`, `git`, `http`, …), not LLM catalog nodes — golden E2E would fail for “wrong reasons.”
- Docs said “CTRR 4 dims”; **production already used 5 profile dims** (ADR-002 keys). Soft gate (CAR-15) needed a clear score contract.

CAR-14 is **prompt + light validation align** — not soft gate, not full English UI, not golden cases.

---

## 2. Grill decisions we locked (before coding)

| # | Decision |
|---|----------|
| 1 | Keep the **5 live dims** (`motivation_goal`, `background_transfer`, `learning_velocity`, `hands_on_proof`, `constraints`). No schema cutover to Conceptual/Technical/Readiness/Resourcefulness. |
| 2 | Write diagnosis + validation prompt/templates in **English** here. CAR-16 owns UI/product-copy only. |
| 3 | Shared Judge + Finalize; **thin per-goal Interviewer briefs** by `goal_id`. |
| 4 | Validation = EN templates + keyword banks for LLM seed nodes — no validation UX/graph redesign. |
| 5 | Expose `profile_score = mean(5 dim confidences)` for CAR-15. No cutoff / warnings / lean prune yet. |
| 6 | EN the deterministic fallback bank (`FOLLOW_UP_BANK`); keep it goal-agnostic. |
| 7 | Exit bar = smoke + unit tests + **4 synthetic fixtures** (1/goal). Full golden suite stays CAR-18. |

Follow-ups filed: **CAR-32** (docs reconcile ADR/V2-PLAN wording); **CAR-15** amended to use `profile_score`.

---

## 3. Step-by-step what we shipped

### Step A — Rewrite diagnosis system prompts (EN + LLM audience)

**File:** `apps/backend/src/career_forge/ai/prompts/diagnosis_interview.py`

- Rewrote `JUDGE_SYSTEM`, `INTERVIEWER_SYSTEM`, `FINALIZE_SYSTEM` in English.
- Audience: BASE/PSP **early ↔ staff**, LLM tracks — not enterprise hiring theater.
- Finalize explicitly forbids legacy SWE gap checklists (`git` / `http` / `db`).
- Added `GOAL_INTERVIEWER_BRIEFS` — one short brief per goal with “what good evidence looks like,” early probes, and staff probes.
- Helper `interviewer_brief_for_goal(goal_id)` for payload injection.

### Step B — Inject per-goal brief into the Interviewer payload

**File:** `apps/backend/src/career_forge/ai/payloads/diagnosis_interview.py`

- `build_interviewer_user_message` now includes a `## goal_brief` section.
- Payload chrome moved to English (`Round`, `final_instructions`, etc.).
- Heuristic regexes kept **PT + EN** so mid-cutover answers still map (negatives, hours/week, “no constraints”).

### Step C — Soft-gate contract: `profile_score`

**Files:**

- `schemas/diagnosis_interview.py` — `BeliefState.mean_confidence()`
- `schemas/diagnosis.py` — `DiagnosisResponse.profile_score` (0–1)
- `schemas/llm_outputs.py` — `to_diagnosis_response(profile_score=…)`
- `ai/llm/diagnosis_interview.py` — finalize sets `profile_score=belief.mean_confidence()`

CAR-15 will soft-gate when `profile_score < cutoff`. CAR-14 only **publishes the number**.

### Step D — English fallback interview script

**File:** `apps/backend/src/career_forge/ai/interview/script.py`

Production still uses the deterministic 2-round script for questions (LLM Interviewer path exists but graph uses the script). We translated:

- `COMPOUND_ROUND_ONE`
- `FOLLOW_UP_BANK` (all 5 dims)
- Round labels → “Practice and routine” / “Context and constraints”

Also updated backend dimension labels/descriptions to EN, and mirrored them in the FE skeleton (`apps/frontend/src/lib/profile-dimensions.ts`) so sidebar copy matches. Optional `profile_score` on the FE `DiagnosisResponse` type.

### Step E — Light validation align

**Files:** `services/assessment_rubric.py`, `services/validation.py`, `ai/graphs/validation.py`

1. EN question templates / labels / hints (`concept` / `application` / `deepening`).
2. Added `RUBRIC_KEYWORDS` for **all 28** LLM catalog seed nodes (7 × 4 tracks), e.g. `rag-grounding`, `agent-tool-use`, `evals-llm-judge`, `ft-lora`.
3. Kept legacy SWE keyword banks for old tests.
4. EN’d fallback validation / mentor summary strings in the validation graph.

No redesign of the validation graph (still deterministic keyword scoring).

### Step F — Tests + fixtures

**New:** `apps/backend/tests/test_car14_recalibration.py`

For each of the 4 goals:

- Mock finalize → belief keys stay the 5 dims; `profile_score` matches mean confidence.
- Gaps must **not** contain legacy SWE markers.
- Goal-specific gap text from the mock still present.
- Interviewer brief exists with Early/Staff probes.
- Validation keywords resolve for one seed node per goal.

Updated existing script / payload / OpenAI finalize tests for EN chrome and `profile_score`.

### Step G — Product doc note

**File:** `docs/product/DIAGNOSIS-INTERVIEW.md`

Short status + prompts outline: English, 5 dims, goal briefs, `profile_score`. Full ADR/V2-PLAN “4 CTRR dims” wording cleanup is **CAR-32**.

---

## 4. What we deliberately did *not* do

| Out of scope | Owner |
|--------------|--------|
| Soft-gate cutoff, lean forge prune, warning UI | CAR-15 |
| Full English UI / remaining PT surfaces | CAR-16 |
| Must-have forge enforcement + ≥70% harness | CAR-17 |
| 16 golden cases + Yuri spot-check | CAR-18 |
| Migrate schema to 4 Conceptual/Technical/… dims | Deferred (not filed) |
| Mentor redesign | Out of F2 |

---

## 5. How to picture the runtime after CAR-14

```text
Screen 1 intake (goal_id + motivation + XP [+ CV])
        │
        ▼
 Judge seeds / updates BeliefState (5 dims, EN prompts)
        │
        ▼
 Interview questions (deterministic EN script today;
                      LLM path gets goal_brief if used)
        │
        ▼
 Finalize → DiagnosisResponse
              ├── strengths / gaps (LLM-track, EN)
              ├── starting_priorities / estimated_mastery
              └── profile_score = mean(5 confidences)  ← CAR-15 input
        │
        ▼
 Forge (unchanged path) · Validation keywords now hit LLM nodes
```

---

## 6. Verification we ran

| Check | Result |
|-------|--------|
| `make test` | 286 passed |
| `make smoke` / agent-verify | VERIFIED + `/health` + `/docs` |
| UI product sync | **Skipped** — copy/locale only, no paradigm change |

---

## 7. Related links

- Linear: [CAR-14](https://linear.app/career-forge-v2/issue/CAR-14)
- Next: [CAR-15 soft gate](https://linear.app/career-forge-v2/issue/CAR-15) · [CAR-16 english UI](https://linear.app/career-forge-v2/issue/CAR-16) · [CAR-32 docs reconcile](https://linear.app/career-forge-v2/issue/CAR-32)
- Spec: [DIAGNOSIS-INTERVIEW.md](../product/DIAGNOSIS-INTERVIEW.md)
- Plan: [V2-PLAN.md](../V2-PLAN.md) § Fase 2
