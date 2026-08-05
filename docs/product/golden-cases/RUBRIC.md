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

Record results in each fixture’s `snapshot.scorecard` or a dated appendix below after the Pedro scoring pass.

## Matrix

4 goals × 4 personas = 16 cases:

| Persona | Soft gate | Coverage bar |
|---------|-----------|--------------|
| soft-gated-weak | on | lean asserts (no ≥70% planner bar) |
| early / mid / staff | off | pre-inject ≥70% |

Dims (`motivation_goal` … `constraints`) appear in `belief_notes` for context — they are **not** matrix axes.

## Appendix — scoring log

_Pending Pedro scoring pass (`make golden-run`). Provisional harness snapshots use `snapshot.source=provisional-harness`._
