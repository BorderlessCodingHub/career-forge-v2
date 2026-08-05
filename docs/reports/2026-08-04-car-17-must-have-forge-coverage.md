# CAR-17 — What we built (step by step)

> **Issue:** [CAR-17](https://linear.app/career-forge-v2/issue/CAR-17) — Must-have enforcement in forge + ≥70% coverage harness  
> **Merged:** 2026-08-04 · PR #21 · `e6a33c0` + `13ecff7` / merge `b761cac`  
> **Follow-ups:** end-task `79801d1`  
> **Phase:** F2 — Goals LLM + prompts + english-first  
> **Class:** [S] after [CAR-8](https://linear.app/career-forge-v2/issue/CAR-8) silence baseline + [CAR-15](https://linear.app/career-forge-v2/issue/CAR-15) soft-gate lean prune

This note explains **what changed and why**, in delivery order — not a line-by-line code tour.

---

## 1. Context — why CAR-17 existed

Phase 2 grill (2026-07-25) locked a product rule: after forge, each of the four LLM goals must land **≥70% of its must-have nodes** in the student graph. That bar is human-QA / harness — not job RAG in the product ([V2-PLAN.md](../V2-PLAN.md)).

Before CAR-17:

- CAR-8 drafted prose must-haves under `docs/product/must-haves/` (10 nodes/goal).
- CAR-15 shipped **catalog-intersection** sidecars in `data/must-haves/` for lean prune only — net-new ids stayed out of the catalog.
- Forge had no structured bias toward must-haves and no post-forge backfill when the LLM skipped them.
- There was no deterministic coverage harness for merge (formal ≥70% on live goldens stays **CAR-18**).

CAR-17 freezes the silence baseline, seeds catalog gaps, wires **bias (A) + inject (B)**, and ships a smoke harness that does **not** need OpenAI.

---

## 2. Locked decisions (grill 2026-08-03/04)

Silence baseline accepted by Pedro (+ agent); Yuri one-round review under CAR-8 had no blocking edits. Spot-check deferred to **CAR-18**.

| # | Decision |
|---|----------|
| 1 | Enforcement = prompt **bias (A)** + post-forge **inject (B)** — not hard fail at student runtime (not C). |
| 2 | Catalog gap seeds ship in the same issue; machine-readable sidecars = **full frozen 10 IDs** per goal. |
| 3 | Coverage metric = presence of must-have `id` in post-forge graph nodes: `\|must_haves ∩ forged_ids\| / \|must_haves\|`. |
| 4 | Acceptance metric measured **pre-inject**; B may bring post-inject coverage to 100%. |
| 5 | CAR-17 scope = wiring + inject + coverage helper + **4 deterministic smoke fixtures**; CAR-18 = 16 golden cases + formal ≥70% acceptance. |
| 6 | ≥70% bar applies to **normal** (non-soft-gated) forge; lean path gets allowlist + post-B sanity only. |
| 7 | Inject = deterministic catalog nodes + edges when prereq already in graph; after GraphExecutor collect, before persist; **no second LLM**. |
| 8 | Bias = structured `must_have_node_ids` on forge input + prompt; normal path keeps **full catalog** (no lean allowlist). |
| 9 | Helper: `services/must_have_coverage.py` + unit tests + `make must-have-coverage`. |
| 10 | Smokes = forged node-id fixtures (no OpenAI required for merge). |
| 11 | Document freeze in `docs/product/must-haves/README.md` + STATUS pointer. |
| 12 | Gap catalog seeds = id + English title + prerequisites (minimal). |
| 13 | Inject B applies to **both** normal and lean paths. |

---

## 3. Step-by-step what we shipped

### Step A — Freeze silence baseline + full sidecars

**Docs:** `docs/product/must-haves/README.md` (+ pt-BR)  
**Data:** `data/must-haves/{rag-engineer,agent-engineer,llm-evals,fine-tuning}.json`

- Documented freeze date **2026-08-04** (Pedro); Yuri spot-check → CAR-18.
- Expanded machine-readable `ids` to the **full 10** per goal (CAR-15 had intersection-only subsets).
- Sidecar note points at silence baseline and CAR-18 deferral.

Example (`rag-engineer`):

```text
rag-embeddings, rag-chunking, rag-retrieval, rag-hybrid-search, rag-rerank,
rag-grounding, rag-eval, rag-orchestration, rag-production, rag-latency-cost
```

### Step B — Catalog gap seeds (10 nodes / track)

**Files:** `data/catalog/*-beginner.json` (×4 tracks)

Must-have ids that were missing from CAR-5 seeds were added as minimal catalog nodes (English title + prerequisites). That makes inject B and lean allowlist able to resolve every frozen id from catalog.

**Follow-up commit** `13ecff7`: `test_catalog_tracks.py` allowed **10** nodes per track (CAR-5 asserted 6–8).

### Step C — Always attach `must_have_node_ids` (bias input)

**File:** `apps/backend/src/career_forge/services/lean_forge.py`

`apply_lean_forge_input()` now:

1. Loads frozen ids via `load_must_have_ids(goal_id)`
2. **Always** sets `must_have_node_ids` on forge GraphRun input (CAR-17 bias)
3. When soft-gated, also sets `lean_allowed_node_ids` (CAR-15 behavior unchanged)

Normal (non-gated) forge keeps the full catalog — bias is preference, not prune.

### Step D — Surface bias in planner context + prompt

**Files:**

- `apps/backend/src/career_forge/services/forge_context.py` — `LearnerForgeContext.must_have_node_ids` + `compact_summary()`
- `apps/backend/src/career_forge/ai/tools/study_plan_planner.py` — prefer those ids as `StudyPlan.node_id` values when listed

This is **enforcement path A**: soft bias through the existing planner, not a second graph.

### Step E — Coverage helper + post-forge inject (B)

**File:** `apps/backend/src/career_forge/services/must_have_coverage.py`

| API | Role |
|-----|------|
| `CoverageResult` | hit / missing / `coverage` / `passed` vs `DEFAULT_COVERAGE_PASS_BAR` (0.70) |
| `compute_must_have_coverage` / `coverage_for_goal` | Pre-inject metric |
| `inject_missing_must_haves` | Append missing catalog nodes; edges only if prereq already present |
| `apply_must_have_inject` | Returns `(post_inject_graph, pre_inject_coverage)` |

Injected nodes: status `BLOQUEADO`, rationale `"Injected must-have (CAR-17)"`. Deterministic — no LLM.

### Step F — Wire inject into `roadmap_forge` (both paths)

**File:** `apps/backend/src/career_forge/ai/graphs/roadmap_forge.py`

After planner/revise (and optional lean allowlist filter), before forge tail events / persist:

1. Resolve `must_have_node_ids` from input (else load from sidecars)
2. `apply_must_have_inject(...)` on `final_graph`
3. Tail SSE / output uses the **post-inject** graph

Applies whether or not the run was soft-gated.

### Step G — Deterministic harness + unit tests

| Artifact | Purpose |
|----------|---------|
| `apps/backend/tests/test_car17_must_have_coverage.py` | Unit tests for metric + inject |
| `apps/backend/tests/fixtures/must_have_coverage/*.json` | 4 goal fixtures (~7/10 must-haves → pass ≥70% pre-inject) |
| `scripts/must-have-coverage.sh` | CLI smoke over the 4 fixtures |
| `make must-have-coverage` | Makefile target |

Harness does **not** call OpenAI — fixtures are forged node-id lists only.

### Step H — Docs + STATUS / ROADMAP

- Freeze / wiring notes in product must-have READMEs (EN + pt-BR) and per-goal “Notes for F2” lines
- `data/must-haves/README.md` — CAR-15 prune + CAR-17 bias/inject + harness consumers
- End-task: Linear Done · `docs/STATUS.md` · `docs/ROADMAP.md`

---

## 4. What we deliberately did *not* do

| Out of scope | Owner |
|--------------|--------|
| 16 golden cases + formal ≥70% on live forge | CAR-18 |
| Yuri spot-check of must-have lists | CAR-18 |
| Hard fail / block student when coverage &lt; 70% | Rejected (not C) |
| Second LLM pass to “fix” missing must-haves | Rejected |
| ≥70% bar on lean (soft-gated) path in this issue | Deferred / sanity only |
| Persist pre-inject coverage as a student-facing field | Not required for CAR-17 |
| Retune `SOFT_GATE_CUTOFF` | CAR-18 |

---

## 5. How to picture the runtime after CAR-17

```text
 POST forge start
        │
        ▼
 apply_lean_forge_input()
        ├── must_have_node_ids = frozen 10 ids   ← always (bias A)
        └── if soft_gated → lean_allowed_node_ids (CAR-15)
        │
        ▼
 roadmap_forge via GraphExecutor (same SSE)
        ├── planner sees must_have_node_ids in learner_context
        ├── optional lean filter on accumulated graph
        │
        ▼
 apply_must_have_inject()
        ├── measure coverage PRE-inject  (≥70% bar for harness / CAR-18)
        └── inject missing catalog must-haves (B)  → student artifact
        │
        ▼
 forge tail events + persist (post-inject graph)
```

Coverage formula (definition A):

```text
coverage = |must_haves ∩ forged_ids| / |must_haves|
pass     = coverage ≥ 0.70   # measured before inject
```

---

## 6. Verification we ran

| Check | Result |
|-------|--------|
| Unit tests (`test_car17_must_have_coverage.py`) | Metric + inject + rationale |
| `make must-have-coverage` | 4/4 fixtures PASS at ≥70% pre-inject |
| Catalog seed test (10 nodes/track) | `13ecff7` |
| PR #21 merge to `main` | `b761cac` |
| End-task | Linear Done · STATUS + ROADMAP (`79801d1`) |

Formal ≥70% on real forge goldens remains **CAR-18**.

---

## 7. Commits

| SHA | Summary |
|-----|---------|
| `e6a33c0` | Bias, inject, harness, gap seeds, freeze docs |
| `13ecff7` | Allow 10 nodes per catalog track in seed test |
| `b761cac` | Merge PR #21 |
| `79801d1` | End-task STATUS + ROADMAP |

---

## 8. Related links

- Linear: [CAR-17](https://linear.app/career-forge-v2/issue/CAR-17)
- PR: [#21](https://github.com/BorderlessCodingHub/career-forge-v2/pull/21)
- Upstream: [CAR-8 must-have drafts](https://linear.app/career-forge-v2/issue/CAR-8) · [CAR-15 soft gate](https://linear.app/career-forge-v2/issue/CAR-15) · [report](./2026-08-03-car-15-soft-gate-lean-forge.md)
- Downstream: [CAR-18 golden cases + Yuri spot-check](https://linear.app/career-forge-v2/issue/CAR-18)
- Plan: [V2-PLAN.md](../V2-PLAN.md) § Fase 2
- Must-haves: [`data/must-haves/`](../../data/must-haves/) · [`docs/product/must-haves/`](../product/must-haves/)
- Helper: `apps/backend/src/career_forge/services/must_have_coverage.py`
- Harness: `make must-have-coverage` → `scripts/must-have-coverage.sh`
