# Golden cases scoring rubric (CAR-18)

**Audience:** Pedro (all 16) · Yuri spot-check (4 mids)  
**Runbook:** [PEDRO-RUNBOOK.md](./PEDRO-RUNBOOK.md)  
**Cutoff:** [SOFT-GATE-CUTOFF.md](./SOFT-GATE-CUTOFF.md)

## Scorecard A–E (per case)

| ID | Criterion | Pass rule |
|----|-----------|-----------|
| **A** Soft gate | `soft_gated` matches persona (weak=true; early/mid/staff=false) at current cutoff | yes/no |
| **B** Spectrum fit | Persona level feels right (gaps + forge/lean shape) | 1–3; need ≥2 |
| **C** Must-haves | non-weak: pre-inject coverage ≥70%; weak: lean allowlist ok | yes/no |
| **D** Validation | Sample question sensible for goal + level (EN) | yes/no |
| **E** English | User-visible snapshot text is English | yes/no |

**Case PASS** ⟺ A+C+D+E pass **and** B ≥ 2.

Canonical scores live in each fixture’s `snapshot.scorecard`. Summary below.

## Matrix

4 goals × 4 personas = 16 cases:

| Persona | Soft gate | Coverage bar |
|---------|-----------|--------------|
| soft-gated-weak | on | lean asserts (no ≥70% planner bar) |
| early / mid / staff | off | pre-inject ≥70% |

Dims (`motivation_goal` … `constraints`) appear in `belief_notes` for context — they are **not** matrix axes.

## Appendix — scoring log (2026-08-05)

**Method:** `make golden-run ALL=1 LIVE=1` → fill A–E (Pedro provisional PASS).  
**Note:** live `graph_ready` is **post-inject**, so reported coverage is often **1.0** (including weak). Soft-gate still judged via seed `profile_score` / `expectations.soft_gated`. Planner-quality ≥70% remains enforced for non-weak by harness history + CAR-17 inject contract.

| Case | A | B | C | D | E | Overall |
|------|---|---|---|---|---|---------|
| rag-engineer__early | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| rag-engineer__mid | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| rag-engineer__staff | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| rag-engineer__soft-gated-weak | ✓ | 2 | ✓ | ✓ | ✓ | **PASS** |
| agent-engineer__early | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| agent-engineer__mid | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| agent-engineer__staff | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| agent-engineer__soft-gated-weak | ✓ | 2 | ✓ | ✓ | ✓ | **PASS** |
| llm-evals__early | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| llm-evals__mid | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| llm-evals__staff | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| llm-evals__soft-gated-weak | ✓ | 2 | ✓ | ✓ | ✓ | **PASS** |
| fine-tuning__early | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| fine-tuning__mid | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| fine-tuning__staff | ✓ | 3 | ✓ | ✓ | ✓ | **PASS** |
| fine-tuning__soft-gated-weak | ✓ | 2 | ✓ | ✓ | ✓ | **PASS** |

**16/16 PASS** · awaiting Yuri spot-check on 4 mids + must-have lists ([YURI-SPOTCHECK.md](./YURI-SPOTCHECK.md)).
