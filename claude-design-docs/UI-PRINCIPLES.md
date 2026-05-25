# UI Principles — Career OS

> How the product should *feel*. Tokens: [design-tokens.md](./design-tokens.md) · Prototype: [`prototype/`](./prototype/)

---

## Visual DNA

### roadmap.sh minimalism (baseline)

- Calm dark canvas, generous whitespace, clear hierarchy
- One primary action per screen
- Dev-friendly — feels like a tool, not a course marketplace
- Reference mood: [roadmap.sh](https://roadmap.sh) backend beginner — **layout inspiration only**

### Living skill graph (evolution)

- Replace linear checklist with **connected nodes** + dependency lines
- Each node: title, status pill, mastery % when known
- Locked nodes dimmed; current focus highlighted (accent border/glow)
- Graph is the **hero** on `/roadmap` — not a sidebar widget

### What we are NOT

- Generic LMS (progress bars everywhere, module cards)
- Gamification (confetti, XP, streaks, leaderboards)
- ChatGPT clone (full-screen chat with no graph context)
- roadmap.sh 1:1 clone (no adaptive states, no forge, no validation)

---

## Dark dev aesthetic

| Element | Rule |
|---------|------|
| Background | Deep navy `#0B0F19` — not pure black |
| Surfaces | Layered: surface → surface-elevated for depth |
| Accent | Indigo `#6366F1` — CTAs, selection, links |
| Semantic | Green mastery, amber review, sky evidence, slate locked |
| Typography | Inter/Geist sans; JetBrains Mono for timeline/scores/code |
| Motion | Subtle — fade-in timeline items, graph reveal; no bounce/confetti |

Full token table: [design-tokens.md](./design-tokens.md) · CSS: [`prototype/styles.css`](./prototype/styles.css)

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
| `MissionBanner` | Top-of-dashboard next action |
| `ForgeTimelineItem` | reasoning / artifact / decision rows |
| `ChatBubble` | Onboarding + mentor |
| `PrimaryButton` / `GhostButton` | Actions |

When adding a **new** shared pattern (e.g. drawer shell, SSE row variant), document it in [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md) Implementation notes.

---

## Layout conventions

| Screen type | Layout |
|-------------|--------|
| Marketing/entry | Centered hero, max-width ~720px |
| Forge | 40/60 split: timeline left, graph right |
| Dashboard | Graph main + right sidebar (progress, evidence, mentor CTA) |
| Validation | Focus mode — question card dominant, minimal chrome |
| Mentor | Drawer from right on dashboard — contextual, not full page |

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
- [ ] Graph skeleton fills as nodes arrive
- [ ] No generic spinner as primary feedback

**Graph reveal**
- [ ] Transition from forge to full graph feels like completion
- [ ] MissionBanner visible with concrete next topic

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
