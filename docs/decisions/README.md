# Architecture Decision Records (ADRs)

Immutable **business + architecture decisions** for Career Forge. Agents must read relevant ADRs before changing related code.

| ADR | Status | Topic |
|-----|--------|-------|
| [ADR-001](./ADR-001-adaptive-diagnosis-ctrr.md) | **Accepted** | Adaptive diagnosis interview (CTRR + Interviewer/Judge) |

## When to add an ADR

- Product rule that outlives a single Linear issue (audience, AI-first constraint, rubric model)
- Replacing a prior approach (supersedes section required)
- Cross-cutting decision touching FE + BE + prompts

## When **not** to add an ADR

- Implementation detail covered by `docs/product/` or `docs/engineering/`
- Sprint-only scope already in Linear acceptance criteria

## Agent workflow

1. `AGENTS.md` → find ADR link for your task type
2. Read ADR (**why**) + `docs/product/*` spec (**how**)
3. Cursor rule with matching `globs` activates on file edit
4. Update ADR only via new ADR that **supersedes** — never silent drift
