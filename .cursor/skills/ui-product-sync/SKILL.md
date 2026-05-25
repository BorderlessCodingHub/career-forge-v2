---
name: ui-product-sync
description: Sync claude-design-docs with implemented UI after paradigm changes. Use when finishing UI work, when asked to "sync UI product docs", or when prototype vs code diverged.
---

# UI product sync

Keep [PRODUCT-SOURCE-OF-TRUTH.md](../../claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md) aligned with `apps/frontend/` and the Claude Design prototype.

Rule: [.cursor/rules/ui-product-sync.mdc](../../.cursor/rules/ui-product-sync.mdc)

---

## When to run

- End of any session that touched `apps/frontend/`, `claude-design-docs/`, Tailwind, or global CSS
- User says: *sync UI product docs*, *update source of truth*, *document UI drift*
- Stop hook flagged UI file changes

---

## Steps

### 1. Gather current state

Read:

1. [PRODUCT-SOURCE-OF-TRUTH.md](../../claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md)
2. [UX-FLOW.md](../../claude-design-docs/UX-FLOW.md)
3. [SCREEN-INTENT.md](../../claude-design-docs/SCREEN-INTENT.md)
4. Relevant screen in [`prototype/Career Forge.html`](../../claude-design-docs/prototype/Career%20Forge.html) (tokens/components — flow may lag)
5. Changed files: `git diff origin/main...HEAD -- apps/frontend claude-design-docs`

### 2. Compare trilogy

| View | Question |
|------|----------|
| Prototype | What was the intended layout, copy, wow moment? |
| Code | What shipped? |
| CHECKPOINT | Does it still serve P0 demo? |

Apply hierarchy from PRODUCT-SOURCE-OF-TRUTH § Source-of-truth hierarchy.

### 3. Update docs (only what changed)

| If… | Then update… |
|-----|----------------|
| Route/flow changed | UX-FLOW + SCREEN-INTENT + SCREEN-INTENT-MAP |
| Colors/type/spacing changed | design-tokens.md + UI-PRINCIPLES if pattern new |
| Code intentionally differs from prototype | PRODUCT-SOURCE-OF-TRUTH → Implementation notes row |
| New shared component | UI-PRINCIPLES component table + Implementation notes |
| Product scope shifted | docs/CHECKPOINT.md (separate issue if major) |

### 4. Report

```
UI product sync complete
- Docs updated: <list>
- Paradigm changes: <summary or "none — cosmetic only">
- Open drift: <items needing Linear issue, or "none">
```

---

## Do not

- Weaken Forge / Validation / Adaptive wow without CHECKPOINT approval
- Leave Implementation notes empty when code diverges from prototype on purpose
