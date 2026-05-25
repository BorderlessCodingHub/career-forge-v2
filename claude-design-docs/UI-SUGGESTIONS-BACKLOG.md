# UI suggestions backlog — Career Forge prototype

Structured log for user-provided UI feedback (images, descriptions) before implementing in the functional mock or Next.js app.

**Process:** User sends image or description → add under **Pending** → agent implements → move to **Applied** with date/issue.

**Related:** [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) · [MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md) · [UI-PRINCIPLES.md](./UI-PRINCIPLES.md)

---

## Applied

| Date | Source | Summary | Implemented in |
|------|--------|---------|----------------|
| 2026-05-25 | User reference images | Borderless Community theming (Code Breakers + logo) | Docs: BORDERLESS-THEMING, design-tokens, UI-PRINCIPLES, PRODUCT-SOT; prototype `styles.css` CSS vars (Phase 1 partial) |

---

## Pending

_Add new items below. Format:_

```markdown
### YYYY-MM-DD — Short title
- **Source:** (image path in `references/` or description)
- **Screen/area:** (e.g. steady canvas, forge timeline, validation)
- **Request:** (what should change)
- **Priority:** (optional: P0 / P1 / nice-to-have)
```

*(empty — add user feedback here)*

---

## This batch (2026-05-25)

Captured from HAC-23 Borderless theming task:

1. **Theming = Borderless Community** — reference images:
   - `references/borderless-code-breakers-dashboard.png`
   - `references/borderless-logo-brand.png`
2. **App shell** — sidebar + top bar + canvas (Code Breakers reference)
3. **Roadmap nodes** — purple cards (`#6B4CE6`) + cyan/mint progress bar (`#2DD4BF` / `#00E5C0`)
4. **Career Forge flow unchanged** — editable diagnosis → forge stream (timeline only) → reveal → steady canvas
5. **Prototype goal** — functional mock aligned to Borderless theming for future Next.js UI ([MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md))

---

## How to contribute

Send screenshots or short descriptions in chat. An agent will:

1. Copy images to `claude-design-docs/references/` (descriptive filename)
2. Add a **Pending** entry
3. Implement when scheduled in MOCK-PROTOTYPE-PLAN or a Linear issue
4. Move to **Applied** on merge

---

*Maintained by agents during UI sessions · see [.cursor/rules/ui-product-sync.mdc](../.cursor/rules/ui-product-sync.mdc)*
