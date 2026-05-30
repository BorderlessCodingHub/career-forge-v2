# UI Principles — Career Forge

> How the product should *feel*. Tokens: [design-tokens.md](./design-tokens.md) · **Borderless:** [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) · Prototype: [`prototype/`](./prototype/)

---

## Visual DNA

### Borderless Community (primary — HAC-23)

Career Forge lives inside the **Borderless** ecosystem. Steady-state UI should match the Code Breakers dashboard mood: deep purple-black canvas, fixed sidebar, top search bar, node-based roadmap on a dot grid.

| Element | Rule |
|---------|------|
| Background | `#0D0B14` deep purple-black — not navy `#0B0F19` |
| Nodes | Vibrant purple cards `#6B4CE6` with cyan/mint progress `#2DD4BF` |
| Accent | Logo purple `#7C3AED` — CTAs, active nav pill |
| Connections | Dashed grey lines with arrowheads |
| Canvas | Dot grid; zoom controls bottom-left; minimap bottom-right |

**References:** [borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png) · [borderless-logo-brand.png](./references/borderless-logo-brand.png)

Full token table + component specs: [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md)

### roadmap.sh minimalism (layout baseline)

- Calm dark canvas, generous whitespace, clear hierarchy
- One primary action per screen
- Dev-friendly — feels like a tool, not a course marketplace
- Reference mood: [roadmap.sh](https://roadmap.sh) backend beginner — **layout inspiration only**

### Goal picker — minimal first screen (HAC-24)

- **Layout:** Narrow column (~560px), no centered hero block
- **Cards:** Text-only row buttons — title + "Em breve" for disabled tracks
- **No chrome:** Skip icons, domain counts, sprout meta, sparkles footer
- **Motivation:** Single textarea + inline char count; CTA right-aligned
- **Typography:** 32px headline (not 44px); step label in mono uppercase

### Onboarding diagnostic — pill rounds (HAC-24)

- **Not chat bubbles** — batch 2 questions per round in pill cards
- Each pill: tag label + prompt + textarea
- 3 rounds: seniority/context → stack/domain → gaps mapping
- Sidebar shows live "O que a IA está mapeando" checklist

### Steady-state roadmap canvas (HAC-21 + Borderless + HAC-24)

- **Code Breakers–style canvas** — purple rounded topic nodes, progress bar at bottom, dashed dependency lines
- **Vertical spine layout (HAC-24)** — central dashed spine, nodes alternate left/right, category headers on spine (Fundamentos → Backend Core → Integração)
- Layout combines roadmap.sh spine with Borderless node styling
- Each node: title, status pill, mastery % / progress bar when known
- Locked nodes dimmed; current focus highlighted (purple glow + mint accent)
- Roadmap is the **hero** on `/roadmap` — full canvas area inside Borderless app shell
- **Optional AI sidebar** (Explain, Test knowledge, Chat) — right panel inside shell; user opens when needed

References: [borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png) (colors + shell) · [roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) (AI sidebar layout only)

### What we are NOT

- Generic LMS (progress bars everywhere, module cards)
- Gamification (confetti, XP, streaks, leaderboards)
- ChatGPT clone (full-screen chat with no graph context)
- roadmap.sh 1:1 clone (no adaptive states, no forge, no validation)

---

## Dark dev aesthetic (Borderless)

| Element | Rule |
|---------|------|
| Background | Deep purple-black `#0D0B14` — textured dark, not pure black |
| Surfaces | Layered: surface → surface-elevated; nodes use `surface-node` purple |
| Accent | Purple `#7C3AED` — CTAs, active nav; mint `#2DD4BF` — progress, evidence |
| Semantic | Green mastery, amber review, mint evidence, slate locked |
| Typography | Inter/Geist sans; JetBrains Mono for timeline/scores/code |
| Motion | Subtle — fade-in timeline items, canvas reveal; no bounce/confetti |

Full token table: [design-tokens.md](./design-tokens.md) · [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) · CSS: [`prototype/styles.css`](./prototype/styles.css)

---

## Borderless app shell

| Region | Rule |
|--------|------|
| **Sidebar** | Fixed left ~240px; BORDERLESS logo; nav list; active item = solid purple pill |
| **Top bar** | Search (⌘K hint), calendar/utilities, sign out — above canvas |
| **Main canvas** | Dot grid background; roadmap nodes; pan/zoom |
| **Floating controls** | Zoom +/- and fit — bottom-left of canvas |
| **Minimap** | Small roadmap preview — bottom-right |
| **Forge stream** | Timeline in content area; **no canvas nodes** until reveal |
| **AI panel** | Optional right sidebar inside shell — not full-page chat |

Prototype evolution: [MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md) · User feedback: [UI-SUGGESTIONS-BACKLOG.md](./UI-SUGGESTIONS-BACKLOG.md)

---

## Language

- **All user-facing copy: Portuguese (Brazil)**
- Tone: confident, direct, supportive — not corporate, not infantil
- Prefer evidence language: *"evidência de aprendizado"*, *"validar mastery"*, *"próxima missão"*
- Error/empty states in PT-BR with actionable next step

Agent-facing docs and code comments: English OK.

---

## Component patterns (prototype → Next.js)

Reuse names from [`prototype/components.jsx`](./prototype/components.jsx):

| Component | Use |
|-----------|-----|
| `SkillNodeCard` | Graph nodes + detail panel |
| `StatusPill` | All six status enums |
| `ScoreRing` | Validation result 0–100 |
| `ForgeTimelineItem` | reasoning / artifact / decision rows |
| `ChatBubble` | Onboarding + mentor |
| `PrimaryButton` / `GhostButton` | Actions |
| `DeployBadge` | Global fixed footer (`z-auto`) — deploy SHA/time + API health dot; stays **below** drawers (`z-40`/`z-50`); `local dev` when build env unset |
| `ChecklistProgress` | Shared study progress UI — `compact` (canvas card: `x/y` + thin mint bar) or `full` (drawer: label, bar, disclaimer); driven by `checklist_completed` / `checklist_total` |
| `ArtifactChromeContext` | Client provider in `ArtifactShellLayout`; `/roadmap` sets `trailSummary` for topbar |
| `ArtifactShell` topbar | Right cluster `items-end` (actions baseline with track title); single `mentor-report-link` ghost action (`topbarActionClass`, `h-9`); optional `trail-study-summary`; track name right |
| `MentorAvatar` | Brand gradient `from-accent-mint to-accent` — `MentorDrawer` header only |
| `VerticalSpineSkeleton` | Loading placeholder for artifact spine (`vertical-spine-skeleton`) |
| `NodeDrawer` study checklist | Right drawer: collapsible sections default open, compact mentor row, sticky `validate-node-cta`; Escape + focus return; **does not** gate validation |
| `SkillNode` (canvas) | Uniform purple card — title, description, optional `ChecklistProgress` compact when checklist items exist; no mastery % on card |
| Dismiss icon button | Square `h-9 w-9`, `text-red-400`, hover/focus `red-900/60` on dark elevated surfaces (drawer close); row delete uses lighter `text-red-500` + `red-500/10` (`EditableDiagnosis`) — same family, different weight |

When adding a **new** shared pattern (e.g. drawer shell, SSE row variant), document it in [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md) Implementation notes.

---

## Layout conventions

| Screen type | Layout |
|-------------|--------|
| **All routes** | Fixed bottom `DeployBadge` (~32px, `z-auto`); root `body` uses `pb-8` so CTAs are not covered; overlays (node drawer, mentor drawer) use `z-40`/`z-50` and stack above the badge |
| Marketing/entry | Centered hero, max-width ~720px |
| Editable diagnosis | Structured lists, full-width, single CTA "Gerar roadmap" |
| Forge (during stream) | **Timeline only** — centered or full-width column, numbered steps 1–N |
| Forge reveal | Animation overlay → vertical roadmap materializes |
| Roadmap steady state | `ArtifactShell` topbar: track name, `mentor-report-link`, optional `trail-study-summary`; page subtitle only (no duplicate `<h1>`); `VerticalSpineSkeleton` loading; spine + uniform nodes; **click node** → accordion drawer + sticky validate CTA; mentor via compact drawer link only |
| Validation | Focus mode — question card dominant, minimal chrome |
| Mentor | AI sidebar or drawer on roadmap — contextual, not full page |

Desktop-first **1280px**. Mobile responsive nice-to-have for hackathon.

---

## Accessibility (minimum)

- Contrast: text-primary on bg passes WCAG AA for body text
- Status not color-only: pills include label text (e.g. "revisar", not just amber dot)
- Focus rings on interactive nodes and CTAs
- `data-screen` / `data-testid` on key regions for Gate B Playwright

---

## Hero moment checklist

Before merging UI for these screens, verify against prototype:

**Live Roadmap Forge**
- [ ] Timeline items appear sequentially (not all at once)
- [ ] Steps numbered 1–N during generation only
- [ ] **No graph/map visible during stream**
- [ ] No generic spinner as primary feedback

**Animation reveal**
- [ ] Stream items fly into vertical roadmap positions
- [ ] Transition feels like completion — no confetti
- [ ] Mission/next action visible after reveal

**Mastery validation**
- [ ] Headline: provar aprendizado, not "quiz"
- [ ] Result shows score + acertou / melhorar / próximo passo
- [ ] Optional collapsed mentor_summary

---

## Implementation mapping

| Prototype | Next.js target |
|-----------|----------------|
| `data-screen` attributes | App Router routes |
| `styles.css` variables | `tailwind.config.ts` theme |
| `FORGE_SCRIPT` mock | `EventSource` SSE consumer |
| Hash nav in `app.jsx` | Real routes + demo mode seed |

Handoff checklist in [brief-v1.md](./brief-v1.md) §5.
