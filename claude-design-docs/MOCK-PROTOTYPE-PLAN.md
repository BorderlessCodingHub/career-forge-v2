# Mock prototype plan — Career Forge HTML prototype

How [`prototype/`](./prototype/) evolves from legacy indigo chrome toward Borderless Community visual language. UX flow remains [UX-FLOW.md](./UX-FLOW.md) (HAC-21).

**Feedback backlog:** [UI-SUGGESTIONS-BACKLOG.md](./UI-SUGGESTIONS-BACKLOG.md)  
**Visual spec:** [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md)

---

## Current state

| Aspect | Prototype today | Target |
|--------|-----------------|--------|
| Colors | Legacy indigo/navy (`#6366F1`, `#0B0F19`) | Borderless purple-black + mint (HAC-23) |
| Shell | Top breadcrumb nav only | Sidebar + top bar + canvas |
| Steady state | Artifact mode — full-width vertical roadmap, click-to-drawer | Code Breakers + roadmap.sh (HAC-25 ✅ partial) |
| Flow | `setup` vs `artifact` modes in `app.jsx` | HAC-21 + HAC-25 |
| Forge nodes | Status-colored during build | Uniform purple during build (HAC-25 ✅) |
| Forge layout during stream | Split timeline + graph (legacy) | **Timeline only** per UX-FLOW — split is documented drift until Phase 4 |

Entry: `cd claude-design-docs/prototype && python3 -m http.server 8765` → `http://localhost:8765/`

---

## Phase 1 — Token / CSS reskin (minimal)

**Goal:** Swap CSS variables to Borderless palette without rewriting JSX screens.

**Files:** `prototype/styles.css` (`:root` variables)

**Tasks:**

- [x] Replace `--bg`, `--surface`, `--accent`, glows with Borderless tokens (HAC-23)
- [ ] Tune hardcoded `rgba(99,102,241,...)` in component classes to purple/mint equivalents (incremental)
- [ ] Update ambient `body::before` gradients to mint + purple
- [ ] Verify contrast on pills and forge banner

**Done when:** Opening prototype feels purple/mint dark, not indigo navy.

**Issue link:** HAC-23

---

## Phase 2 — App shell wrapper

**Goal:** Introduce Borderless layout chrome around existing screens.

**Files:** `prototype/app.jsx`, new `prototype/shell.jsx` (or inline), `styles.css` (`.sidebar`, `.topbar`, `.canvas-main`)

**Tasks:**

- [ ] Fixed left sidebar: BORDERLESS wordmark, nav placeholders (Dashboard, Roadmap, Settings)
- [ ] Top bar: search stub, sign out
- [ ] Route screens render in `canvas-main` content area
- [ ] Forge / onboarding can use simplified shell (no sidebar minimap)

**Reference:** [borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png)

**Done when:** All screens mount inside shell; nav highlights active route.

---

## Phase 3 — Steady state canvas (artifact mode) — partial HAC-25

**Goal:** Finished-trail artifact — roadmap.sh focus, not setup dashboard.

**Files:** `app.jsx`, `screens-dashboard.jsx`, `skill-graph.jsx`, `components.jsx` (`NodeDetailSidebar`), `styles.css`

**Tasks:**

- [x] `setup` vs `artifact` app modes — hide stepper in artifact
- [x] Remove default sidebar clutter (progress, evidence, mentor) from artifact canvas
- [x] Uniform purple nodes on canvas (`uniform` prop)
- [x] Click node → right drawer (description, references, Ask AI, validate CTA)
- [x] Drawer study checklist — task/reference checkboxes + progress bar (HAC-63; Next.js only, prototype lags)
- [ ] Cyan progress bar on nodes (deferred — status lives in drawer per HAC-25)
- [ ] Dot grid background + zoom/minimap stubs
- [ ] Full Borderless app shell (Phase 2)

**Done when:** `/roadmap` feels like opening your personalized roadmap.sh page.

**Issue link:** HAC-25 (prototype) · HAC-9 (Next.js)

---

## Phase 4 — Forge + reveal alignment

**Goal:** Timeline-only forge inside shell; reveal animates into canvas nodes.

**Files:** `prototype/screens-forge.jsx`, `app.jsx` routes

**Tasks:**

- [ ] Remove graph preview during stream (HAC-21)
- [ ] Reveal targets canvas node positions (not legacy SVG graph only)
- [ ] Editable diagnosis screen (replace read-only result)

**Issue link:** HAC-18 / HAC-8 UI

---

## Incremental improvements

After each phase, user feedback goes to [UI-SUGGESTIONS-BACKLOG.md](./UI-SUGGESTIONS-BACKLOG.md) **Pending** → implement → **Applied**.

Do not batch unrelated visual changes without backlog entries.

---

## Handoff to Next.js (`apps/frontend`)

When monorepo lands (HAC-5, HAC-9):

1. Copy token table → `tailwind.config.ts`
2. Port shell layout → `app/(app)/layout.tsx`
3. Canvas → React Flow + Borderless node components
4. Register divergences in [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md) Implementation notes

---

*HAC-23 · 2026-05-25*
