# CAR-18 — Pedro runbook (golden scoring pass)

**Issue:** [CAR-18](https://linear.app/career-forge-v2/issue/CAR-18)  
**Audience:** Pedro (author + scorer of all 16 cases)  
**Grill lock date:** 2026-08-05 · harness landed with CAR-18

This is **your** path only: refine fixtures → scoring pass → rubric → cutoff confirm → Yuri handoff.  
CI never calls OpenAI; it only checks what you freeze into git.

Commands:

```bash
make golden-check
make golden-run CASE=rag-engineer__mid
make golden-run ALL=1
make golden-run ALL=1 LIVE=1   # needs OPENAI_API_KEY
```

Docs: [RUBRIC.md](./RUBRIC.md) · [SOFT-GATE-CUTOFF.md](./SOFT-GATE-CUTOFF.md) · [YURI-SPOTCHECK.md](./YURI-SPOTCHECK.md) · template `data/golden_cases/_TEMPLATE.json`

---

## Locked decisions (do not reopen without a new grill)

| # | Decision |
|---|----------|
| 1 | Matrix = **4 goals × 4 spectrum personas** (early / mid / staff / soft-gated-weak). 5 profile dims are **scored inside** cases, not matrix axes. |
| 2 | **Hybrid:** LLM only on your scoring pass; CI = deterministic checks on frozen snapshots. |
| 3 | Official path = **script + fixtures** (not 16× browser). Browser only for debug. |
| 4 | **Split:** diagnosis quality = human rubric; script feeds forge + validation from a **hand-seeded** `DiagnosisResponse`. |
| 5 | **≥70% pre-inject** must-have coverage required on the **12 non-weak** cases. Soft-gated-weak prove gate + lean, not the 70% planner bar. |
| 6 | Rubric scorecard **A–E** (see below). Pass = A+C+D+E pass and B ≥ 2. |
| 7 | Yuri: **4 mid** cases (1/goal) + must-have list review; no mandatory UI. |
| 8 | Soft-gate cutoff = **midpoint** between max(weak `profile_score`) and min(early). Global bar. |
| 9 | Files: `data/golden_cases/*.json` + docs under `docs/product/golden-cases/`. |

Goals: `rag-engineer` · `agent-engineer` · `llm-evals` · `fine-tuning`.

---

## Scorecard (rubric A–E)

Fill one row per case (into `snapshot.scorecard` or [RUBRIC.md](./RUBRIC.md) appendix).

| ID | Criterion | How you judge | Pass |
|----|-----------|---------------|------|
| **A** | Soft gate | Expected `soft_gated` matches persona (weak=true; others=false) given current cutoff | yes/no |
| **B** | Spectrum fit | early / mid / staff “feels” right (gaps + lean vs full forge) | 1–3 + ≤2 lines |
| **C** | Must-haves | non-weak: pre-inject coverage ≥ 70%; weak: lean allowlist / gate path ok | yes/no |
| **D** | Validation | One generated question is sensible for goal + level (smoke) | yes/no |
| **E** | English | User-visible outputs are EN | yes/no |

**Case passes** iff A, C, D, E = pass **and** B ≥ 2.

Suggested `profile_score` bands for hand-seeds (shipped skeletons already use these):

| Persona | Target `profile_score` |
|---------|------------------------|
| soft-gated-weak | 0.35 – 0.45 (shipped **0.42**) |
| early | 0.55 – 0.65 (shipped **0.58**) |
| mid | 0.70 – 0.80 (shipped **0.75**) |
| staff | 0.85 – 0.95 (shipped **0.90**) |

Keep a clear gap between max(weak) and min(early). Current default cutoff **0.50** — see [SOFT-GATE-CUTOFF.md](./SOFT-GATE-CUTOFF.md).

---

## Naming

```text
{goal_id}__{persona}.json
```

Examples: `rag-engineer__early.json`, `rag-engineer__soft-gated-weak.json` → **16 files** (already generated; refine in place).

---

## End-to-end checklist

### 0. Preconditions

- [x] `main` has CAR-14…17 merged.
- [ ] Stack healthy if using `--live`: `make up` + `curl` `/health`.
- [ ] `.env` has `OPENAI_API_KEY` only for `LIVE=1`.
- [x] Must-have SoT frozen: `data/must-haves/*.json`.
- [x] Cutoff default **0.50** (retuned from golden seeds).

### 1. Refine the 16 personas (no LLM required)

Edit each `data/golden_cases/{goal}__{persona}.json`:

1. **Meta** — blurb (who is this BASE/PSP person?).
2. **Transcript context** — short Q/A for rubric notes only (not fed to Judge).
3. **Hand-seed `diagnosis`** — keep explicit `profile_score` in band; update strengths/gaps.
4. **`belief_notes`** — optional dim context for scoring.
5. **`expectations`** — `soft_gated` + `min_pre_inject_coverage` (`0.7` or `null` for weak).

Do **not** invent must-have ids; use `data/must-haves/{goal}.json`.  
Template: `data/golden_cases/_TEMPLATE.json`.

### 2. Soft-gate sanity on seeds (deterministic)

```bash
make golden-check
```

Confirm weak → gated, early/mid/staff → not gated. If wrong, **move the seed’s score**, then re-check recommended midpoint.

### 3. Scoring pass — forge snapshots

**Refresh coverage only (no OpenAI):**

```bash
make golden-run ALL=1
```

**Live forge (rewrites `forged_node_ids`):**

```bash
make golden-run CASE=rag-engineer__mid LIVE=1
make golden-run ALL=1 LIVE=1
```

Budget: up to **16** forge LLM runs. Re-run only cases you change. LangSmith optional — not SoT.

Provisional harness snapshots ship with `snapshot.source=provisional-harness` (≥70% on non-weak). Replace with `live-forge` when you run `--live`.

### 4. Fill the scorecard (all 16)

Mark A–E + overall PASS/FAIL in `snapshot.scorecard` or the rubric appendix. Fix failures before Yuri.

### 5. Confirm / retune `SOFT_GATE_CUTOFF`

`make golden-check` prints `recommended_midpoint`. If seeds moved, update:

- `DEFAULT_SOFT_GATE_CUTOFF` + `.env.example`
- [SOFT-GATE-CUTOFF.md](./SOFT-GATE-CUTOFF.md)

### 6. CI freeze check

```bash
make golden-check
make must-have-coverage
make test   # includes test_car18_golden_cases.py
```

### 7. Yuri handoff

1. Four `*__mid.json` cases.
2. Fill [YURI-SPOTCHECK.md](./YURI-SPOTCHECK.md).
3. Ask Yuri to ack scorecards + must-have lists.
4. Record date/outcome (doc or Linear CAR-18 comment).

### 8. Close CAR-18

- [x] 16 fixtures in `data/golden_cases/`
- [x] Rubric + runbook + Yuri template
- [x] Automated `golden-check` green
- [x] ≥70% / live forge snapshots (post-inject coverage on live path)
- [x] Cutoff retuned + documented (0.50)
- [x] Pedro scorecards filled (2026-08-05 — 16/16 PASS)
- [ ] Yuri spot-check recorded
- [ ] Linear → Done via end-task

---

## What you are *not* doing

- Running OpenAI inside every CI job.
- Scoring Conceptual/Technical/Readiness/Resourcefulness as schema keys.
- Requiring Yuri to click through the UI.
- Treating LangSmith as acceptance SoT.
- Mentoring flows (out of F2 scope).
- Requiring pre-inject ≥70% on soft-gated-weak cases.

---

## Quick reference — persona intent

| Persona | Soft gate | Forge shape | Coverage bar |
|---------|-----------|-------------|--------------|
| soft-gated-weak | on | lean | lean/gate asserts; no 70% planner bar |
| early | off | normal | pre-inject ≥70% |
| mid | off | normal | pre-inject ≥70% (Yuri sample) |
| staff | off | normal | pre-inject ≥70% |

---

## Related

- [V2-PLAN.md](../../V2-PLAN.md) § Fase 2  
- [must-haves/README.md](../must-haves/README.md)  
- Soft gate: `apps/backend/src/career_forge/services/soft_gate.py`  
- Coverage: `make must-have-coverage` · Golden: `make golden-check` / `make golden-run`
