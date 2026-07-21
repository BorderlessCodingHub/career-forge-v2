# Architecture Decision Records (ADRs)

Immutable **business + architecture decisions** for Career Forge. Agents must read relevant ADRs before changing related code.

| ADR | Status | Topic |
|-----|--------|-------|
| [ADR-001](./ADR-001-adaptive-diagnosis-ctrr.md) | **Accepted · binding in v2** | Adaptive diagnosis (CTRR + Interviewer/Judge) |
| [ADR-002](./ADR-002-universal-profile-framework.md) | **Not active in v2 F2** | Universal 5-dimension profile (historical; do not implement) |

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
