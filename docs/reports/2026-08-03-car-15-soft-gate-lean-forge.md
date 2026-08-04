# CAR-15 — What we built (step by step)

> **Issue:** [CAR-15](https://linear.app/career-forge-v2/issue/CAR-15) — Soft gate: global CTRR bar + lean forge prune + warnings  
> **Merged:** 2026-08-03 · PR #20 · `3308f41` / merge `48d65b4`  
> **Follow-ups:** end-task `89559d3` · ui-product-sync `a45c934`  
> **Phase:** F2 — Goals LLM + prompts + english-first  
> **Class:** [S] after [CAR-14](https://linear.app/career-forge-v2/issue/CAR-14) (`profile_score` contract)

This note explains **what changed and why**, in delivery order — not a line-by-line code tour.

---

## 1. Context — why CAR-15 existed

Phase 2 grill (2026-07-25) locked a pilot rule: learners who finish diagnosis **below the bar** still continue — but the forge builds a **leaner** roadmap and the UI shows a warning. Hard block is deferred to v2.1 after score calibration.

CAR-14 already published the input number:

```text
profile_score = mean(confidence of 5 live profile dims)
```

CAR-15 consumes that number and adds:

1. A **global cutoff** (`SOFT_GATE_CUTOFF`, provisional **0.55**)
2. **Lean prune** of forge catalog input (must-haves ∩ catalog + one foundation hop)
3. **Warning UI** on diagnosis edit + forge entry (copy + flag only)

Without CAR-15, every learner got the full forge regardless of diagnosis confidence.

---

## 2. Locked decisions (from Linear / V2-PLAN F2.5–F2.10)

| # | Decision |
|---|----------|
| 1 | One **global** bar for all 4 goals — not per-goal cutoffs. |
| 2 | Gate fires when `profile_score < cutoff` (not XP years, not “4 CTRR dims”). |
| 3 | Cutoff is **provisional** `0.55`; retune on 16 golden cases (**CAR-18**). |
| 4 | Lean forge = **same** `GraphExecutor` + same SSE stream UX — not a second cheap graph. |
| 5 | Prune = must-haves + **one** foundation layer (direct `prerequisites`) — not % shrink, not must-haves-only. |
| 6 | Warning = copy + `soft_gated` flag on diagnosis summary **and** forge entry — no new layout paradigm. |
| 7 | Soft gate **does not block** confirm / forge in the pilot. |

---

## 3. Step-by-step what we shipped

### Step A — Soft-gate service (bar + runtime fields)

**File:** `apps/backend/src/career_forge/services/soft_gate.py`

- `evaluate_soft_gate(diagnosis)` → `SoftGateDecision(soft_gated, soft_gate_warning)`
- Cutoff from env `SOFT_GATE_CUTOFF` (default `0.55`); documented in `.env.example`
- **Fail-open:** if `profile_score` was never set (`not in model_fields_set`) → no gate (legacy / pre-CAR-14 payloads)
- **Explicit `0.0`** → gated (distinct from “missing score”)
- `enrich_diagnosis_soft_gate()` attaches `soft_gated` / `soft_gate_warning` for API responses
- `diagnosis_dump_for_persist()` strips soft-gate fields (and unset `profile_score`) so JSONB storage stays clean — gate is **derived at read/forge time**, not frozen in the profile

English warning copy (API-owned):

> Your diagnosis confidence is below our bar — we'll build a leaner roadmap focused on must-have foundations. You can still continue.

### Step B — Schema surface for FE + API

**File:** `apps/backend/src/career_forge/schemas/diagnosis.py`

Added optional runtime fields on `DiagnosisResponse`:

- `soft_gated: bool`
- `soft_gate_warning: str | None`

Mirrored on FE: `apps/frontend/src/types/contracts.ts`.

### Step C — Wire enrichment at diagnosis boundaries

Soft-gate fields are computed whenever diagnosis is returned to the client:

| Path | Behavior |
|------|----------|
| Diagnosis interview finalize | `enrich_diagnosis_soft_gate` after finalize (`diagnosis_interview` graph) |
| `/me` profile read | Enrich stored diagnosis before response (`me_profile.py`) |
| Profile confirm persist | Persist **without** soft-gate fields (`profile_diagnosis.py` + `diagnosis_dump_for_persist`) |

Confirm round-trips preserve “missing vs explicit score” so legacy fail-open survives.

### Step D — Machine-readable must-have sidecars

**Dir:** `data/must-haves/`

One JSON per LLM goal (`rag-engineer`, `agent-engineer`, `llm-evals`, `fine-tuning`):

```json
{
  "goal_id": "rag-engineer",
  "ids": ["rag-embeddings", "rag-chunking", …],
  "note": "CAR-15: catalog-seed intersection … Net-new ids deferred to CAR-17."
}
```

These are the **catalog intersection** of the prose must-have docs under `docs/product/must-haves/`. Net-new node ids (not yet in catalog seeds) stay out until **CAR-17**.

Resolver: `paths.must_haves_dir()` (+ optional `MUST_HAVES_DIR` override for tests).

### Step E — Lean forge prune service

**File:** `apps/backend/src/career_forge/services/lean_forge.py`

1. `load_must_have_ids(goal_id)` — read sidecar JSON  
2. `compute_lean_allowlist(goal_id, track_id)`:
   - Start from must-have ids **present in the catalog**
   - Add each must-have’s **direct** `prerequisites` (one hop only — e.g. must-have `c` with prereq `b` → `{c, b}`, not transitive `a`)
3. `apply_lean_forge_input(forge_input)`:
   - Evaluate soft gate from embedded diagnosis
   - If gated and allowlist non-empty → attach `lean_allowed_node_ids`
   - If gated but allowlist empty → **fail-open** (full catalog; log warning)
   - If not gated → strip lean keys; full forge

### Step F — Same forge path, filtered catalog

**Files:** `api/forge.py`, `ai/graphs/roadmap_forge.py`

- Forge API merges inputs then runs `apply_lean_forge_input` before starting the GraphRun
- `build_accumulated_graph(..., allowed_node_ids=…)` skips catalog nodes outside the allowlist
- Stream intro/tail/planner paths all call `resolve_lean_allowed_node_ids(input_data)`
- Study-plan final graph is filtered to the allowlist when lean is active

**Unchanged:** GraphExecutor, SSE event types, forge timeline UX. Lean is input pruning, not a parallel graph.

### Step G — Warning UI (presentation only)

**New:** `apps/frontend/src/components/diagnosis/SoftGateWarningBanner.tsx`

- Renders API `soft_gate_warning` with “Lean roadmap” status chrome
- `role="status"` — informational, not a modal / blocker

Wired at:

| Screen | Test id | Source |
|--------|---------|--------|
| `/onboarding/edit` (`EditableDiagnosis`) | `soft-gate-warning` | `diagnosis.soft_gated` + warning from API |
| `/forge` entry | `soft-gate-warning-forge` | stored diagnosis session |

Confirm / “Generate roadmap” / forge stream still work when gated.

### Step H — Tests

**New:** `apps/backend/tests/test_car15_soft_gate.py`

Covers:

- Missing score → fail-open  
- Explicit `0.0` / below cutoff → gated  
- At/above cutoff → full forge  
- Persist dump omits soft-gate fields + unset score  
- Must-have load + one-hop prereq allowlist  
- Empty allowlist → fail-open  
- `apply_lean_forge_input` attaches allowlist  
- `build_accumulated_graph` respects allowlist size/ids  

### Step I — Docs + design sync

- `docs/V2-PLAN.md` F2.8 — cutoff `0.55` provisional  
- `docs/product/DIAGNOSIS-INTERVIEW.md` — soft-gate status line  
- `docs/product/must-haves/README.md` — CAR-15 vs CAR-17 wiring note  
- After merge: STATUS / ROADMAP end-task; **ui-product-sync** for SoftGateWarningBanner in PRODUCT-SOURCE-OF-TRUTH / UX-FLOW / SCREEN-INTENT  

---

## 4. What we deliberately did *not* do

| Out of scope | Owner |
|--------------|--------|
| Retune cutoff on 16 golden cases | CAR-18 |
| Full must-have set + ≥70% post-forge coverage harness | CAR-17 |
| Hard block below bar | v2.1 (post-calibration) |
| Second “cheap” forge graph or different stream UX | Rejected |
| Per-goal cutoffs | Rejected (F2.5) |
| Net-new must-have catalog nodes | CAR-17 |
| Persist `soft_gated` in profile JSONB | Rejected (runtime-derived) |

---

## 5. How to picture the runtime after CAR-15

```text
Finalize /me / confirm
        │
        ▼
 DiagnosisResponse (+ profile_score from CAR-14)
        │
        ▼
 enrich_diagnosis_soft_gate()
        ├── profile_score missing     → soft_gated=false (fail-open)
        ├── profile_score < 0.55      → soft_gated=true + warning copy
        └── profile_score ≥ 0.55      → soft_gated=false
        │
        ├──────────────────────────────┐
        ▼                              ▼
 FE: SoftGateWarningBanner        Persist: strip soft_gated /
     (edit + forge entry)               warning from JSONB
        │
        ▼
 POST forge start
        │
        ▼
 apply_lean_forge_input()
        ├── not gated → full catalog
        └── gated → lean_allowed_node_ids
                    = must-haves∩catalog ∪ direct prereqs
                    (empty allowlist → fail-open full)
        │
        ▼
 roadmap_forge via GraphExecutor (same SSE)
        └── build_accumulated_graph(allowed_node_ids=…)
```

---

## 6. Verification we ran

| Check | Result |
|-------|--------|
| Unit tests (`test_car15_soft_gate.py`) | Bar + prune + allowlist graph filter |
| PR #20 merge to `main` | `48d65b4` |
| End-task | Linear Done · STATUS + ROADMAP |
| UI product sync | Soft-gate banner noted in design docs (`a45c934`) |

Cutoff remains **provisional** until CAR-18 golden retune.

---

## 7. Related links

- Linear: [CAR-15](https://linear.app/career-forge-v2/issue/CAR-15)
- Upstream: [CAR-14 CTRR recalibration](https://linear.app/career-forge-v2/issue/CAR-14) · [report](./2026-08-02-car-14-ctrr-recalibration.md)
- Downstream: [CAR-17 must-have harness](https://linear.app/career-forge-v2/issue/CAR-17) · [CAR-18 golden cases](https://linear.app/career-forge-v2/issue/CAR-18)
- Plan: [V2-PLAN.md](../V2-PLAN.md) § F2.5–F2.10 / F2.8
- Spec: [DIAGNOSIS-INTERVIEW.md](../product/DIAGNOSIS-INTERVIEW.md)
- Must-haves: [`data/must-haves/`](../../data/must-haves/) · [`docs/product/must-haves/`](../product/must-haves/)
