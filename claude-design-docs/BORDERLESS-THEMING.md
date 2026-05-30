# Borderless theming — Career Forge

> **Canonical visual language** for Career Forge within the Borderless ecosystem. Agents read this before UI work alongside [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md).

**Navigation:** [design-tokens.md](./design-tokens.md) · [UI-PRINCIPLES.md](./UI-PRINCIPLES.md) · [MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md) · [UI-SUGGESTIONS-BACKLOG.md](./UI-SUGGESTIONS-BACKLOG.md)

---

## Reference images

| File | What it shows |
|------|----------------|
| [references/borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png) | Borderless Community **Code Breakers** — app shell, sidebar, canvas roadmap, purple nodes, cyan progress |
| [references/borderless-logo-brand.png](./references/borderless-logo-brand.png) | Borderless logo — mint/cyan-green + purple interlocking ribbon on dark textured background |
| [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) | **Secondary** — vertical spine + optional AI sidebar (layout only; colors follow Borderless) |

---

## Brand intent

Career Forge shares Borderless Community’s dark, premium dev-tool aesthetic. Steady-state roadmap should feel like **Code Breakers** (node canvas on dot grid), not generic indigo LMS chrome. Product flow stays HAC-21; only visual shell and tokens change.

---

## Color tokens

| Token | Hex | CSS variable | Usage |
|-------|-----|--------------|-------|
| `bg` | `#0D0B14` | `--bg` | App background, canvas base |
| `bg-sidebar` | `#0A0812` | `--bg-sidebar` | Fixed left sidebar panel |
| `surface` | `#15121F` | `--surface` | Cards, inputs, top bar |
| `surface-elevated` | `#1C1828` | `--surface-elevated` | Modals, drawers, hover panels |
| `surface-node` | `#6B4CE6` | `--surface-node` | Roadmap topic nodes (vibrant purple) |
| `border` | `#2A2540` | `--border` | Borders, dashed connection lines |
| `border-soft` | `#1F1A30` | `--border-soft` | Subtle dividers |
| `text-primary` | `#FFFFFF` | `--text` | Headings, node titles |
| `text-secondary` | `#9CA3AF` | `--text-2` | Labels, nav inactive, hints |
| `text-muted` | `#6B7280` | `--text-3` | Meta, timestamps |
| `accent` | `#7C3AED` | `--accent` | CTAs, active nav pill, logo purple |
| `accent-mint` | `#2DD4BF` | `--accent-mint` | Progress fill, logo mint, highlights |
| `accent-mint-bright` | `#00E5C0` | `--accent-mint-bright` | Progress bar peak, glow accents |
| `accent-glow` | `rgba(124, 58, 237, 0.22)` | `--accent-glow` | Focus rings, node selection |
| `mint-glow` | `rgba(45, 212, 191, 0.18)` | `--mint-glow` | Progress bar track glow |
| `success` | `#22C55E` | `--success` | Mastery / aprovado (semantic) |
| `warning` | `#F59E0B` | `--warning` | Revisar / atenção |
| `locked` | `#4B5563` | `--locked` | Nó bloqueado |
| `evidence` | `#2DD4BF` | `--evidence` | Evidências (align with mint accent) |
| `grid-dot` | `rgba(255,255,255,0.04)` | — | Canvas dot grid (24px spacing) |

### Gradients (logo-derived)

- **Brand ribbon:** `linear-gradient(135deg, #2DD4BF 0%, #7C3AED 100%)` — logo mark, hero accents
- **Node progress:** `linear-gradient(90deg, #00E5C0, #2DD4BF)` — fill inside node progress bars
- **Ambient mesh:** subtle purple + mint radial at canvas edges (low opacity)

---

## Layout — Borderless app shell

```
┌──────────┬────────────────────────────────────────────────────┐
│ Sidebar  │ Top bar: search (⌘K) · calendar · sign out          │
│ (fixed)  ├────────────────────────────────────────────────────┤
│ Logo     │                                                    │
│ Nav      │  Main canvas — dot grid, roadmap nodes             │
│ items    │  [zoom +/- fit] bottom-left  [minimap] bottom-right │
│          │                                                    │
│ Profile  │                                                    │
└──────────┴────────────────────────────────────────────────────┘
```

| Region | Spec |
|--------|------|
| **Sidebar** | ~240px fixed left; darker than main bg; nav items with icon + label; **active item** = solid purple pill (`--accent` bg, white text) |
| **Top bar** | Full width above canvas; search input rounded, muted border; utility actions right |
| **Canvas** | Full remaining viewport; dot grid background; pannable/zoomable (React Flow style in production) |
| **Zoom controls** | Floating stack bottom-left: +, −, fit view |
| **Minimap** | Small preview bottom-right on canvas |
| **AI sidebar** (Career Forge) | Optional right panel inside shell — Explain / Test / Chat; collapsible; does not replace canvas |

Reference: [borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png)

---

## Component specs

### Roadmap node (steady state)

| Property | Value |
|----------|-------|
| Shape | Rounded rectangle, ~12–16px radius |
| Background | `--surface-node` (`#6B4CE6`) |
| Title | White, 14–15px semibold |
| Progress bar | Track: dark purple inset; fill: `--accent-mint` → `--accent-mint-bright` |
| Border | None or 1px `rgba(255,255,255,0.08)` |
| Selected | `--accent-glow` outer glow + `--accent` border |

### Connections

| Property | Value |
|----------|-------|
| Style | Dashed, 1.5–2px |
| Color | `#4B5563` or `--border` |
| Arrow | Small arrowhead at target node |
| Active path | Optional mint tint on completed prerequisites |

### Search bar (top)

- Rounded full or large radius input
- Placeholder muted grey; icon left; shortcut hint `⌘ K` right inside field
- Background: `--surface` slightly lighter than canvas

### Status pills (Career Forge semantic)

Keep HAC-21 status enum; map colors to Borderless where possible:

| Status | Pill treatment |
|--------|----------------|
| `bloqueado` | `--locked` muted |
| `recomendado` | `--accent` purple soft bg |
| `em_estudo` | `--accent-mint` soft bg |
| `validar` | `--warning` |
| `aprovado` | `--success` |
| `revisar` | `--warning` stronger |

---

## Career Forge flow mapping (unchanged)

UX flow from [UX-FLOW.md](./UX-FLOW.md) does **not** change:

1. Goal → Onboarding → **Editable diagnosis** → Gerar roadmap
2. **Forge stream** — timeline only, no graph on canvas during generation
3. **Animation reveal** — stream items animate into node positions on canvas
4. **Steady state** — Code Breakers–style canvas (not legacy indigo skill-graph dashboard)

| Phase | Shell behavior |
|-------|----------------|
| Marketing / goal / onboarding | Borderless shell optional; centered content OK |
| Editable diagnosis | Full-width content inside shell or simplified chrome |
| Forge stream | Timeline column; **hide canvas nodes** until reveal |
| Reveal | Canvas fades in; nodes materialize from stream |
| Steady `/roadmap` | `ArtifactShell` topbar (track name, `mentor-report-link`, optional trail study summary) + vertical spine canvas; mentor via node drawer; **no** duplicate page `<h1>` |

### Artifact topbar + mentor (Next.js — 2026-05-28)

| Element | Spec |
|---------|------|
| **`MentorAvatar`** | `bg-gradient-to-br from-accent-mint to-accent` — brand ribbon; used in `MentorDrawer` header |
| **`trail-study-summary`** | `text-accent-mint text-xs` — aggregate checklist topics started (`x/y tópicos com estudo iniciado`); not mastery % |
| **Topbar ghost actions** | Shared `topbarActionClass` — `h-9` bordered pill, `hover:bg-surface`; `h-7` leading slot (centered `FileText`); right cluster `items-end` so actions align to track title baseline |
| **Spine selection** | Active row dot: `border-accent-mint`, `shadow-[0_0_12px_var(--mint-glow)]` |
| **Loading** | `vertical-spine-skeleton` pulse placeholders — not a lone text spinner |

See [design-tokens.md](./design-tokens.md) · Implementation notes in [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md).

---

## Do / Don't

### Do

- Use deep purple-black backgrounds (`#0D0B14` family)
- Use vibrant purple nodes and cyan/mint progress fills
- Implement fixed sidebar + top search bar for steady state
- Use dot grid on roadmap canvas
- Keep Portuguese (Brazil) copy and HAC-21 wow moments
- Map Tailwind theme to tokens in [design-tokens.md](./design-tokens.md)

### Don't

- Revert to indigo/navy Career Forge tokens (`#6366F1`, `#0B0F19`) for new UI
- Use generic LMS cards, confetti, or leaderboard chrome
- Show skill graph / canvas nodes during forge stream
- Treat roadmap.sh reference as color authority (layout only)
- Rename skill status enums without CHECKPOINT update

---

## Implementation checklist

- [ ] `tailwind.config.ts` maps all tokens above
- [ ] App shell component: sidebar + topbar + canvas slot
- [ ] Steady state: React Flow (or equivalent) with purple nodes + dashed edges
- [ ] Prototype Phase 1: [MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md) — CSS variables in `prototype/styles.css`
- [ ] User feedback: append to [UI-SUGGESTIONS-BACKLOG.md](./UI-SUGGESTIONS-BACKLOG.md)

---

*HAC-23 — Borderless visual language for Career Forge · 2026-05-25 · artifact topbar + mentor avatar: 2026-05-28*
