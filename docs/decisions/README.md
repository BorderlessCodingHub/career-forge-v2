# Architecture Decision Records (ADRs)

Immutable **business + architecture decisions** for Career Forge. Agents must read relevant ADRs before changing related code.

| ADR | Status | Topic |
|-----|--------|-------|
| [ADR-001](./ADR-001-adaptive-diagnosis-ctrr.md) | **Accepted · binding in v2** | Adaptive diagnosis (CTRR loop brand + Interviewer/Judge) |
| [ADR-002](./ADR-002-universal-profile-framework.md) | **Keys live in prod** | 5 profile dims (`motivation_goal` … `constraints`); no F2 schema migration |
| [ADR-003](./ADR-003-forge-recovery-auth-scaffold.md) | **Accepted** (timing / free forge → ADR-005) | Forge recovery + auth scaffold (pre-Borderless) |
| [ADR-004](./ADR-004-canonical-skill-content.md) | **Accepted** | Canonical skill content — forge refs N:1, not per-run posts |
| [ADR-005](./ADR-005-identity-gate-product-entry.md) | **Accepted** | Identity gate at product entry · paywall before diagnosis (CAR-57) |
| [ADR-006](./ADR-006-sign-out-jti-revocation.md) | **Accepted** | Sign out + JWT jti revocation |
| [ADR-007](./ADR-007-reference-viewer.md) | **Accepted** | Reference viewer `/reference` — not overlay, not `/learn` |

v2 execution decisions (cost pool, auth platform, goals): [V2-PLAN.md](../V2-PLAN.md) decision log.

## When to add an ADR

- Product rule that outlives a single Linear issue (audience, AI-first constraint, rubric model)
- Replacing a prior approach (supersedes section required)
- Cross-cutting decision touching FE + BE + prompts

## When **not** to add an ADR

- Implementation detail covered by `docs/product/` or `docs/engineering/`
- Phase-only scope already in Linear acceptance criteria or V2-PLAN

## Agent workflow

1. `AGENTS.md` → find ADR link for your task type
2. Read ADR (**why**) + `docs/product/*` spec (**how**)
3. Cursor rule with matching `globs` activates on file edit
4. Update ADR only via new ADR that **supersedes** — never silent drift
