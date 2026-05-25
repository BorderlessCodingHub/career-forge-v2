# Design tokens — Career Forge

Extraídos do prototype Claude Design (`prototype/styles.css`).

## Colors

| Token | Hex | Uso |
|-------|-----|-----|
| `bg` | `#0B0F19` | Background principal |
| `surface` | `#131825` | Cards, panels |
| `surface-elevated` | `#1A2236` | Modals, drawers |
| `border` | `#2A3348` | Bordas sutis |
| `text-primary` | `#F1F5F9` | Títulos, body |
| `text-secondary` | `#94A3B8` | Labels, hints |
| `accent` | `#6366F1` | CTA, seleção, links |
| `success` | `#22C55E` | Mastery / aprovado |
| `warning` | `#F59E0B` | Revisar / atenção |
| `locked` | `#475569` | Nó bloqueado |
| `evidence` | `#38BDF8` | Evidências, artifacts |

## Typography

- **Sans:** Inter (UI)
- **Mono:** JetBrains Mono (timeline, código, scores)

## Status pills

| Status | Cor | Significado |
|--------|-----|-------------|
| `bloqueado` | locked | Prerequisite não cumprido |
| `recomendado` | accent | Prioridade atual |
| `em_estudo` | text-secondary | Em progresso |
| `validar` | evidence | Pronto para entrevista IA |
| `aprovado` | success | Mastery validado |
| `revisar` | warning | Falhou validação |

## Spacing

Grid 4px: 4, 8, 12, 16, 24, 32, 48

## Radius

- Cards: 8px
- Modals: 12px
- Pills: full

## Componentes reutilizáveis (prototype)

Definidos em `prototype/components.jsx`:

- `SkillNodeCard`
- `StatusPill`
- `ScoreRing`
- `MissionBanner`
- `ForgeTimelineItem`
- `ChatBubble`
- `PrimaryButton` / `GhostButton`
