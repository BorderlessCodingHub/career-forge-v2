# Design tokens — Career Forge (Borderless)

> **Canonical palette:** [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) · CSS: [`prototype/styles.css`](./prototype/styles.css) · App: `apps/frontend/src/app/globals.css`

Brand kit (CAR-34 grill 2026-08-12): `#121212` / `#5316CC` / `#2DEBB1` from official [borderlesscoding.com](https://borderlesscoding.com) logo SVG. **Retired:** `#44D5AD`, legacy `#0D0B14` / `#7C3AED` / `#2DD4BF`.

## Colors

| Token | Hex | Usage |
|-------|-----|-----|
| `bg` | `#121212` | Main background, canvas base |
| `bg-sidebar` | `#0A0A0A` | Fixed sidebar / artifact topbar |
| `surface` | `#1A1A1A` | Cards, inputs, top bar |
| `surface-elevated` | `#222222` | Modals, drawers |
| `surface-node` | `#5316CC` | Roadmap nodes (brand purple) |
| `border` | `#2E2E2E` | Borders, dashed lines |
| `border-soft` | `#1F1F1F` | Subtle dividers |
| `text-primary` | `#FFFFFF` | Headings, body |
| `text-secondary` | `#9CA3AF` | Labels, hints |
| `text-muted` | `#6B7280` | Meta, timestamps |
| `accent` | `#5316CC` | CTA, active nav, logo purple |
| `accent-mint` | `#2DEBB1` | Progress, evidence, logo mint |
| `accent-mint-bright` | `#5AF5C8` | Progress bar peak |
| `success` | `#22C55E` | Mastery / approved |
| `warning` | `#F59E0B` | Review / attention |
| `locked` | `#4B5563` | Locked node |
| `evidence` | `#2DEBB1` | Evidence, artifacts (mint) |

### Brand assets (Next.js)

| Asset | Path | Use |
|-------|------|-----|
| Logo SVG | `public/brand/borderless-logo.svg` | `BrandMark` — artifact topbar |
| Favicon | `public/brand/favicon.ico` | `metadata.icons` in root layout |

Paths respect `NEXT_PUBLIC_BASE_PATH` via `brandAssetPath()` (`src/lib/brand-assets.ts`).

### Dismiss / destructive icon (implemented — dark UI)

Not separate hex tokens; Tailwind red scale on `surface-elevated`:

| Role | Classes (Next.js) | Use |
|------|-------------------|-----|
| Default | `text-red-400` | Drawer/modal close **✕** |
| Hover / focus bg | `hover:bg-red-900/60`, `focus-visible:ring-red-500/50` | `NodeDrawer` header close |
| Row delete (lighter) | `text-red-500`, `hover:bg-red-500/10` | `EditableDiagnosis` pencil/trash |

Prototype still uses muted `.slideover-close` — intentional drift; see [PRODUCT-SOURCE-OF-TRUTH](./PRODUCT-SOURCE-OF-TRUTH.md) Implementation notes.

### Mentor avatar (brand ribbon — Next.js)

| Role | Classes | Use |
|------|---------|-----|
| Avatar fill | `bg-gradient-to-br from-accent-mint to-accent` | `MentorAvatar` in `MentorDrawer` header |

Aligns with [BORDERLESS-THEMING](./BORDERLESS-THEMING.md) logo-derived ribbon; replaces legacy `sky-400` / `indigo-500` mentor chips.

### Artifact topbar ghost actions (Next.js)

| Role | Classes | Use |
|------|---------|-----|
| Control shell | `h-9`, `topbarActionClass` | `mentor-report-link` in artifact topbar |
| Leading slot | `h-7 w-7` | Icon box with centered `FileText` (`h-4 w-4`) |
| Brand mark | `BrandMark` size 36 | Replaces Lucide `Axe` placeholder |

### Spine branch connectors (artifact canvas — Next.js)

| Role | Spec | Use |
|------|------|-----|
| Default | 2px solid `bg-border` | `roadmap-connector-{id}` — card to spine dot |
| Revisar | 2px solid `bg-warning` | Node status `revisar` |
| Selected | 2px solid `bg-accent-mint` | Active spine row selection |

### Trail progress ring (artifact page intro)

| Role | Classes | Use |
|------|---------|-----|
| Progress ring | ~44px SVG, `stroke-accent-mint`, center `%` label `text-[10px]` | `trail-progress-ring` in **page intro** (below subtitle) — `getTrailChecklistProgressPct`: same per-topic checklist math as canvas, item-pooled across topics (not mastery %, not topic-average) |

### CSS variables (`prototype/styles.css` + `globals.css`)

```css
--bg: #121212;
--bg-sidebar: #0A0A0A;
--surface: #1A1A1A;
--surface-2: #222222;
--surface-node: #5316CC;
--border: #2E2E2E;
--accent: #5316CC;
--accent-mint: #2DEBB1;
--accent-mint-bright: #5AF5C8;
```

## Typography

- **Sans:** Inter (UI)
- **Mono:** JetBrains Mono (timeline, code, scores)

## Status pills

| Status | Color | Meaning |
|--------|-----|-------------|
| `bloqueado` | locked | Prerequisite not met |
| `recomendado` | accent (purple) | Current priority |
| `em_estudo` | accent-mint | In progress |
| `validar` | warning | Ready for AI interview |
| `aprovado` | success | Mastery validated |
| `revisar` | warning | Failed validation |

## Spacing

Grid 4px: 4, 8, 12, 16, 24, 32, 48

## Radius

- Cards / nodes: 12–16px
- Modals: 12px
- Nav active pill: full (999px)
- Pills: full

## Canvas

- Dot grid: 24px spacing, `rgba(255,255,255,0.04)` dots on `--bg`
- Connection lines: solid 2px branch connectors card ↔ spine dot on artifact canvas; central spine 1px `border`

## Reusable components (prototype)

Defined in `prototype/components.jsx`:

- `SkillNodeCard`
- `StatusPill`
- `ScoreRing`
- `MissionBanner`
- `ForgeTimelineItem`
- `ChatBubble`
- `PrimaryButton` / `GhostButton`

---

*HAC-23 — Borderless tokens · 2026-05-25 · CAR-34 rebrand 2026-08-12*
