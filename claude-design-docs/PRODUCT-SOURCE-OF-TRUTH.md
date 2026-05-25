# PRODUCT SOURCE OF TRUTH — Career OS

> **Canonical doc for agents.** Read this before any UI work. Update this when the UI paradigm changes.

**Navigation:** [README](./README.md) · [PRODUCT-VISION](./PRODUCT-VISION.md) · [UI-PRINCIPLES](./UI-PRINCIPLES.md) · [SCREEN-INTENT-MAP](./SCREEN-INTENT-MAP.md) · [CHECKPOINT](../docs/CHECKPOINT.md)

---

## What this doc is

Single place to resolve conflicts between:

1. **Claude Design prototype** — [`prototype/`](./prototype/) (visual + interaction intent)
2. **Implemented UI** — `apps/web/` when it exists (runtime truth for behavior)
3. **Hackathon product goals** — [CHECKPOINT](../docs/CHECKPOINT.md), [handoff context](../docs/handoff_chat_gpt.txt)

Agents compare all three before coding UI. After sessions that change layout, tokens, flows, or component patterns, **update this doc** (and linked docs) so the next agent does not drift.

---

## Source-of-truth hierarchy

When sources conflict, apply this order **unless** an active Linear issue explicitly overrides (scoped to that issue only):

| Priority | Source | Wins when… | Agent action |
|----------|--------|------------|--------------|
| **1** | **Hackathon goals** — [CHECKPOINT](../docs/CHECKPOINT.md) P0 wow features, demo script, out-of-scope | Prototype or code adds scope, weakens AI-as-motor, or breaks 5-min demo | Cut or defer; do not ship |
| **2** | **Screen intent** — [SCREEN-INTENT-MAP](./SCREEN-INTENT-MAP.md) | Prototype detail contradicts wow moment or route purpose | Match intent; prototype is reference not law |
| **3** | **Claude Design prototype** — [`prototype/`](./prototype/), [design-tokens.md](./design-tokens.md) | No implemented UI yet, or implementation diverges without documented reason | Implement to match prototype + tokens |
| **4** | **Implemented UI** — `apps/web/` | Deliberate evolution documented in **Implementation notes** below | Code wins; update docs same session |
| **5** | **Brief history** — [brief-v1.md](./brief-v1.md) | Prototype already evolved past an old prompt | Prefer prototype + this doc over brief |

### Tie-breakers

- **Copy (PT-BR):** Prototype microcopy wins unless CHECKPOINT/demo script requires different wording.
- **Tokens:** [design-tokens.md](./design-tokens.md) wins over ad-hoc hex in JSX/CSS. Tailwind theme must map to tokens.
- **Status enum:** `bloqueado | recomendado | em_estudo | validar | aprovado | revisar` — never rename without updating CHECKPOINT + API contracts.
- **Forge SSE:** Backend event names in CHECKPOINT beat prototype mock labels; UI maps events to prototype timeline visual language.

---

## Product north star (summary)

Full narrative: [PRODUCT-VISION](./PRODUCT-VISION.md)

**Career OS** = AI-native learning operating system for career changers entering tech.

| Pillar | One line |
|--------|----------|
| Skill graph | Dynamic model of the professional — not a static checklist |
| Live Roadmap Forge | User *watches* AI build their personal trail (streaming wow) |
| Mastery validation | Progress only after AI interview proves learning |
| Adaptive planning | Graph reacts to validation outcomes |
| Borderless mentor value | Evidence + gaps for embaixadores, not generic chat |

**Pitch line:** *Sem IA vira checklist. Com IA diagnostica, valida e adapta.*

---

## UI principles (summary)

Full spec: [UI-PRINCIPLES](./UI-PRINCIPLES.md)

- roadmap.sh **minimalism** + **living skill graph** (connected nodes, status, mastery %)
- Dark dev aesthetic — tokens in [design-tokens.md](./design-tokens.md)
- Portuguese (Brazil) for all user-facing copy
- Premium dev-tool feel — no LMS chrome, no confetti/gamification
- Hero moments: **Forge stream + reveal**, **Validation interview + score**

---

## Screen map (summary)

Full table: [SCREEN-INTENT-MAP](./SCREEN-INTENT-MAP.md)

| Route | Must match prototype | Can evolve in code |
|-------|----------------------|-------------------|
| `/` Goal picker | Hero + 3 cards + motivation field | Animation library, form validation UX |
| `/onboarding` | Chat diagnostic, 4–6 Q feel | Streaming vs batch API |
| `/roadmap/forge` | Split timeline + graph skeleton | SSE wiring, scroll behavior |
| `/roadmap/forge/complete` | Reveal + MissionBanner | Motion implementation |
| `/roadmap` | Graph steady state + sidebar | React Flow vs custom SVG |
| `/validate/:topic` | Interview + ScoreRing result | Voice, timer — out of MVP |
| `/roadmap` (adaptive) | Graph state change + mentor drawer | Drawer vs modal |

Prototype entry: [`prototype/Career OS.html`](./prototype/Career%20OS.html) · hash routes in [`prototype/app.jsx`](./prototype/app.jsx)

---

## Linked reference files

| File | Role |
|------|------|
| [brief-v1.md](./brief-v1.md) | Original Claude Design prompts per screen |
| [design-tokens.md](./design-tokens.md) | Color, type, status pills, spacing |
| [prototype/](./prototype/) | Interactive HTML/JSX reference |
| [docs/CHECKPOINT.md](../docs/CHECKPOINT.md) | Stack, wow features, demo script, scope |
| [docs/stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md) | Forge SSE + LangGraph spec |
| [docs/handoff_chat_gpt.txt](../docs/handoff_chat_gpt.txt) | Product debate + judge feedback (context) |

---

## Implementation notes (living)

*Update this section when `apps/web/` diverges from prototype on purpose.*

| Topic | Prototype | Implemented | Decision | Date |
|-------|-----------|-------------|----------|------|
| Monorepo UI | Full prototype in HTML | Not scaffolded | Match prototype when HAC-9 starts | — |
| Forge events | Mock `FORGE_SCRIPT` | SSE from FastAPI (HAC-18) | Map SSE types to timeline UI | — |
| Graph library | Custom JSX nodes | TBD | Prefer prototype layout; library choice open | — |

---

## Agent workflow — before UI work

1. Read this file → [PRODUCT-VISION](./PRODUCT-VISION.md) → [UI-PRINCIPLES](./UI-PRINCIPLES.md) → [SCREEN-INTENT-MAP](./SCREEN-INTENT-MAP.md)
2. Open [`prototype/Career OS.html`](./prototype/Career%20OS.html) for the target screen
3. Read [CHECKPOINT](../docs/CHECKPOINT.md) for P0 scope
4. If `apps/web/` exists, diff against prototype intent — do not blindly diff pixels

## Agent workflow — after UI paradigm change

Update when any of: new shared component pattern, layout shift, token change, new/changed route flow, status UX change.

1. Edit **Implementation notes** table above
2. Update [SCREEN-INTENT-MAP](./SCREEN-INTENT-MAP.md) if routes or must-match changed
3. Update [design-tokens.md](./design-tokens.md) if tokens changed
4. Mention doc updates in commit/PR summary

Rule: [.cursor/rules/ui-product-sync.mdc](../.cursor/rules/ui-product-sync.mdc) · Skill: [.cursor/skills/ui-product-sync/SKILL.md](../.cursor/skills/ui-product-sync/SKILL.md)

---

*Last updated: HAC-20 — initial source-of-truth harness*
