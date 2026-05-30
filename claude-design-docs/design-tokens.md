# Design tokens — Career Forge (Borderless)

> **Canonical palette:** [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) · CSS: [`prototype/styles.css`](./prototype/styles.css)

Extracted from Borderless Community reference (Code Breakers dashboard + logo). Replaces legacy indigo/navy Career Forge tokens (HAC-23).

## Colors

| Token | Hex | Uso |
|-------|-----|-----|
| `bg` | `#0D0B14` | Background principal, canvas base |
| `bg-sidebar` | `#0A0812` | Sidebar fixa |
| `surface` | `#15121F` | Cards, inputs, top bar |
| `surface-elevated` | `#1C1828` | Modals, drawers |
| `surface-node` | `#6B4CE6` | Nós do roadmap (roxo vibrante) |
| `border` | `#2A2540` | Bordas, linhas tracejadas |
| `border-soft` | `#1F1A30` | Divisores sutis |
| `text-primary` | `#FFFFFF` | Títulos, body |
| `text-secondary` | `#9CA3AF` | Labels, hints |
| `text-muted` | `#6B7280` | Meta, timestamps |
| `accent` | `#7C3AED` | CTA, nav ativa, roxo logo |
| `accent-mint` | `#2DD4BF` | Progresso, evidências, mint logo |
| `accent-mint-bright` | `#00E5C0` | Pico da barra de progresso |
| `success` | `#22C55E` | Mastery / aprovado |
| `warning` | `#F59E0B` | Revisar / atenção |
| `locked` | `#4B5563` | Nó bloqueado |
| `evidence` | `#2DD4BF` | Evidências, artifacts (mint) |

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

### Trail study summary (topbar micro-copy)

| Role | Classes | Use |
|------|---------|-----|
| Summary text | `text-accent-mint`, `text-xs` | `trail-study-summary` in artifact topbar — aggregate checklist topics started, not mastery % |

### CSS variables (`prototype/styles.css`)

```css
--bg: #0D0B14;
--bg-sidebar: #0A0812;
--surface: #15121F;
--surface-2: #1C1828;
--surface-node: #6B4CE6;
--border: #2A2540;
--accent: #7C3AED;
--accent-mint: #2DD4BF;
--accent-mint-bright: #00E5C0;
```

## Typography

- **Sans:** Inter (UI)
- **Mono:** JetBrains Mono (timeline, código, scores)

## Status pills

| Status | Cor | Significado |
|--------|-----|-------------|
| `bloqueado` | locked | Prerequisite não cumprido |
| `recomendado` | accent (purple) | Prioridade atual |
| `em_estudo` | accent-mint | Em progresso |
| `validar` | warning | Pronto para entrevista IA |
| `aprovado` | success | Mastery validado |
| `revisar` | warning | Falhou validação |

## Spacing

Grid 4px: 4, 8, 12, 16, 24, 32, 48

## Radius

- Cards / nodes: 12–16px
- Modals: 12px
- Nav active pill: full (999px)
- Pills: full

## Canvas

- Dot grid: 24px spacing, `rgba(255,255,255,0.04)` dots on `--bg`
- Connection lines: dashed `#4B5563` or `--border`

## Componentes reutilizáveis (prototype)

Definidos em `prototype/components.jsx`:

- `SkillNodeCard`
- `StatusPill`
- `ScoreRing`
- `MissionBanner`
- `ForgeTimelineItem`
- `ChatBubble`
- `PrimaryButton` / `GhostButton`

---

*HAC-23 — Borderless tokens · 2026-05-25*
