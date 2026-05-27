# UI Product Sync

Keep product docs aligned with implemented UI after paradigm changes.

## When to run

After any UI session that touched:
- `apps/frontend/`
- `claude-design-docs/`
- Tailwind config or CSS
- Component theming or layout

## Steps

### 1. Gather current state
Read (in order):
- `claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md`
- `claude-design-docs/prototype/` (if relevant)
- `git diff` of frontend changes in this session

### 2. Compare trilogy
Check alignment between:
- **Prototype intent** (claude-design-docs)
- **Implemented code** (apps/frontend)
- **CHECKPOINT** (docs/CHECKPOINT.md)

Identify:
- Route changes (new, removed, renamed)
- Color/token/theming changes
- Intentional divergence from prototype
- New components not yet documented
- Scope shifts

### 3. Update docs (conditionally)
Only update if paradigm actually changed:
- `claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md` — UI truth
- `docs/CHECKPOINT.md` § Frontend routes — if routes changed
- `claude-design-docs/` relevant files — if tokens/components changed

### 4. Report
List what was updated and why.

## Constraints

- Never weaken P0 features without explicit approval:
  - Forge timeline stream
  - Mastery validation
  - Adaptive roadmap
- Don't update docs for minor CSS tweaks — only paradigm changes
- Prototype may intentionally lag implementation; that's OK

## Input
Describe what UI changes were made, or leave blank to auto-detect from git diff.
