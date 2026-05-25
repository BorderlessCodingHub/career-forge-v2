# UI suggestions backlog — Career Forge prototype

Structured log for user-provided UI feedback (images, descriptions) before implementing in the functional mock or Next.js app.

**Process:** User sends image or description → add under **Pending** → agent implements → move to **Applied** with date/issue.

**Related:** [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) · [MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md) · [UI-PRINCIPLES.md](./UI-PRINCIPLES.md)

---

## Applied

| Date | Source | Summary | Implemented in |
|------|--------|---------|----------------|
| 2026-05-25 | User reference images | Borderless Community theming (Code Breakers + logo) | Docs: BORDERLESS-THEMING, design-tokens, UI-PRINCIPLES, PRODUCT-SOT; prototype `styles.css` CSS vars (Phase 1 partial) |
| 2026-05-25 | `references/prototype-onboarding-current.png` | Onboarding: chat bubbles → **pill rounds** (batch questions with inputs); goal picker minimal; vertical roadmap spine; prototype 404 fix | HAC-24: `screens-flow.jsx`, `skill-graph.jsx`, `index.html`, docs |
| 2026-05-25 | Batch 2026-05-25 (forge + trail steady state) | Uniform forge nodes; **artifact mode** on `/roadmap` — no stepper/sidebar clutter; click node → detail drawer with references + Ask AI | HAC-25: `app.jsx`, `screens-dashboard.jsx`, `skill-graph.jsx`, `components.jsx`, `styles.css`, docs |
| 2026-05-25 | HAC-23 theming batch | Borderless shell target; purple nodes + cyan progress; flow unchanged (diagnosis → forge → artifact) | BORDERLESS-THEMING, MOCK-PROTOTYPE-PLAN Phase 1–2 |
| 2026-05-25 | `references/prototype-onboarding-current.png` | Onboarding pill rounds (3×2 Q), not ChatGPT bubbles | HAC-24 + SCREEN-INTENT §2 |
| 2026-05-25 | User feedback (HAC-24) | Goal picker minimal — compact cards, single CTA | HAC-24 + UI-PRINCIPLES |
| 2026-05-25 | `references/roadmap-sh-vertical-ai-tutor.png` | Vertical spine roadmap (left/right nodes, dashed connections) | HAC-24 `skill-graph.jsx` + SCREEN-INTENT §6 |
| 2026-05-25 | HAC-22 rename | Prototype 404 — `Career OS.html` redirect stub (legacy URL only) | `index.html` + redirect stub |
| 2026-05-25 | `references/forge-screen-current.png` | Uniform purple forge nodes during build | HAC-25 `uniform` prop |
| 2026-05-25 | `references/trail-dashboard-polluted-current.png`, `roadmap-sh-reference-full.png` | Artifact steady state — no stepper/sidebar; click node → drawer | HAC-25 artifact mode |

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

## Deferred (implementation backlog, not UI feedback)

| Item | Why deferred | Owner issue |
|------|----------------|-------------|
| Forge timeline-only (no split graph during stream) | Prototype keeps approved split layout until Phase 4 | HAC-18 / MOCK-PROTOTYPE-PLAN Phase 4 |
| Editable diagnosis screen | Hash `#result` placeholder | HAC-8 |
| Full Borderless app shell (sidebar + top bar) | Phase 2 not started | HAC-9 / MOCK-PROTOTYPE-PLAN Phase 2 |

---

## How to contribute

Send screenshots or short descriptions in chat. An agent will:

1. Copy images to `claude-design-docs/references/` (descriptive filename)
2. Add a **Pending** entry
3. Implement when scheduled in MOCK-PROTOTYPE-PLAN or a Linear issue
4. Move to **Applied** on merge

---

*Maintained by agents during UI sessions · HAC-26 backlog compliance audit · see [.cursor/rules/ui-product-sync.mdc](../.cursor/rules/ui-product-sync.mdc)*
