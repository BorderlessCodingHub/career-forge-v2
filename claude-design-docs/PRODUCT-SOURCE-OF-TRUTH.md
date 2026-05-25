# PRODUCT SOURCE OF TRUTH — Career Forge

> **Canonical doc for agents.** Read this before any UI work. Update this when the UI paradigm changes.

**Navigation:** [README](./README.md) · [UX-FLOW](./UX-FLOW.md) · [SCREEN-INTENT](./SCREEN-INTENT.md) · [PRODUCT-VISION](./PRODUCT-VISION.md) · [UI-PRINCIPLES](./UI-PRINCIPLES.md) · [CHECKPOINT](../docs/CHECKPOINT.md)

---

## What this doc is

Single place to resolve conflicts between:

1. **Claude Design prototype** — [`prototype/`](./prototype/) (visual + component reference; **flow may lag** — see UX-FLOW)
2. **Implemented UI** — `apps/web/` when it exists (runtime truth for behavior)
3. **Hackathon product goals** — [CHECKPOINT](../docs/CHECKPOINT.md), [handoff context](../docs/handoff_chat_gpt.txt)

Agents compare all three before coding UI. After sessions that change layout, tokens, flows, or component patterns, **update this doc** (and linked docs) so the next agent does not drift.

---

## Canonical UX flow (HAC-21)

```
Goal → Onboarding chat → Editable diagnosis → [Gerar roadmap] → Forge stream (steps only) → Animation reveal → Vertical roadmap (roadmap.sh) + optional AI sidebar
```

Full screen-by-screen: [UX-FLOW.md](./UX-FLOW.md) · Must-match: [SCREEN-INTENT.md](./SCREEN-INTENT.md)

---

## Source-of-truth hierarchy

When sources conflict, apply this order **unless** an active Linear issue explicitly overrides (scoped to that issue only):

| Priority | Source | Wins when… | Agent action |
|----------|--------|------------|--------------|
| **1** | **Hackathon goals** — [CHECKPOINT](../docs/CHECKPOINT.md) P0 wow features, demo script, out-of-scope | Prototype or code adds scope, weakens AI-as-motor, or breaks 5-min demo | Cut or defer; do not ship |
| **2** | **Screen intent** — [SCREEN-INTENT.md](./SCREEN-INTENT.md) + [UX-FLOW.md](./UX-FLOW.md) | Prototype detail contradicts wow moment or route purpose | Match intent; prototype is reference not law |
| **3** | **Claude Design prototype** — [`prototype/`](./prototype/), [design-tokens.md](./design-tokens.md) | No implemented UI yet, or implementation diverges without documented reason | Tokens/components from prototype; **flow from UX-FLOW** |
| **4** | **Implemented UI** — `apps/web/` | Deliberate evolution documented in **Implementation notes** below | Code wins; update docs same session |
| **5** | **Brief history** — [brief-v1.md](./brief-v1.md) | Prototype already evolved past an old prompt | Prefer UX-FLOW + this doc over brief |

### Tie-breakers

- **Copy (PT-BR):** Prototype microcopy wins unless CHECKPOINT/demo script requires different wording.
- **Tokens:** [design-tokens.md](./design-tokens.md) wins over ad-hoc hex in JSX/CSS. Tailwind theme must map to tokens.
- **Status enum:** `bloqueado | recomendado | em_estudo | validar | aprovado | revisar` — never rename without updating CHECKPOINT + API contracts.
- **Forge SSE:** Backend event names in CHECKPOINT beat prototype mock labels; UI maps events to **timeline-only** stream (no graph during generation).

---

## Product north star (summary)

Full narrative: [PRODUCT-VISION](./PRODUCT-VISION.md)

**Career Forge** = AI-native learning operating system for career changers entering tech.

| Pillar | One line |
|--------|----------|
| Skill graph | Dynamic model of the professional — not a static checklist |
| Live Roadmap Forge | User *watches* AI build their personal trail (streaming timeline → animation reveal) |
| Mastery validation | Progress only after AI interview proves learning |
| Adaptive planning | Graph reacts to validation outcomes |
| Borderless mentor value | Evidence + gaps for embaixadores, not generic chat |

**Pitch line:** *Sem IA vira checklist. Com IA diagnostica, valida e adapta.*

---

## UI principles (summary)

Full spec: [UI-PRINCIPLES](./UI-PRINCIPLES.md)

- roadmap.sh **vertical layout** + **adaptive personalized skill graph** (status, mastery %)
- Dark dev aesthetic — tokens in [design-tokens.md](./design-tokens.md)
- Portuguese (Brazil) for all user-facing copy
- Premium dev-tool feel — no LMS chrome, no confetti/gamification
- Hero moments: **Forge timeline stream**, **Animation reveal**, **Validation interview + score**
- Steady state: vertical roadmap + **optional** AI sidebar (Explain / Test / Chat)

**Layout reference:** [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png)

---

## Screen map (summary)

Full table: [SCREEN-INTENT-MAP.md](./SCREEN-INTENT-MAP.md) · Must-match: [SCREEN-INTENT.md](./SCREEN-INTENT.md)

| Route | Must match | Can evolve in code |
|-------|------------|-------------------|
| `/` Goal picker | Hero + 3 cards + motivation field | Animation library, form validation UX |
| `/onboarding` | Chat diagnostic, 4–6 Q feel | Streaming vs batch API |
| `/onboarding/edit` | **Editable** fortes/lacunas/recomendação + **"Gerar roadmap"** | Drag-reorder, autosave |
| `/roadmap/forge` | **Timeline only** — numbered steps, no graph during stream | SSE wiring, scroll behavior |
| `/roadmap/forge/complete` | Stream items fly into vertical layout | Motion implementation |
| `/roadmap` | **Vertical roadmap** steady state + optional AI sidebar | Node detail panel, sidebar UX |
| `/validate/:topic` | Interview + ScoreRing result | Voice, timer — out of MVP |
| `/roadmap` (adaptive) | Roadmap state change + mentor/AI context | Drawer vs sidebar |

Prototype entry: [`prototype/Career Forge.html`](./prototype/Career%20Forge.html) — **note:** prototype flow is pre-HAC-21; see [UX-FLOW § Prototype drift](./UX-FLOW.md#prototype-drift)

---

## Linked reference files

| File | Role |
|------|------|
| [UX-FLOW.md](./UX-FLOW.md) | Canonical flow + old vs new |
| [SCREEN-INTENT.md](./SCREEN-INTENT.md) | Per-screen must-match |
| [brief-v1.md](./brief-v1.md) | Original Claude Design prompts per screen |
| [design-tokens.md](./design-tokens.md) | Color, type, status pills, spacing |
| [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) | Steady-state layout reference |
| [prototype/](./prototype/) | Component/token reference (flow may lag) |
| [docs/CHECKPOINT.md](../docs/CHECKPOINT.md) | Stack, wow features, demo script, scope |
| [docs/stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md) | Forge SSE + LangGraph spec |

---

## Implementation notes (living)

*Update this section when `apps/web/` diverges from docs on purpose.*

| Topic | Docs (HAC-21) | Prototype (legacy) | Implemented | Decision | Date |
|-------|-----------------|-------------------|-------------|----------|------|
| Post-diagnosis | Editable `/onboarding/edit` | Read-only `/onboarding/result` | Not scaffolded | **Docs win** — skip confirmation dead-end | HAC-21 |
| Forge during stream | Timeline only, no graph | Split timeline + graph skeleton | Not scaffolded | **Docs win** — timeline-only wow | HAC-21 |
| Steady state | Vertical roadmap + optional AI sidebar | Skill graph dashboard | Not scaffolded | **Docs win** — roadmap.sh layout | HAC-21 |
| Reveal | Items fly into vertical layout | Graph panel reveal | Not scaffolded | **Docs win** | HAC-21 |
| Monorepo UI | Full flow per UX-FLOW | Old hash routes in HTML | Not scaffolded | Match docs when HAC-9/HAC-18 start | — |
| Forge events | Mock `FORGE_SCRIPT` | SSE from FastAPI (HAC-18) | Map SSE to timeline UI only | — | — |

---

## Agent workflow — before UI work

1. Read this file → [UX-FLOW](./UX-FLOW.md) → [SCREEN-INTENT](./SCREEN-INTENT.md) → [UI-PRINCIPLES](./UI-PRINCIPLES.md)
2. Open [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) for steady-state target
3. Open [`prototype/Career Forge.html`](./prototype/Career%20Forge.html) for tokens/components (ignore old flow)
4. Read [CHECKPOINT](../docs/CHECKPOINT.md) for P0 scope
5. If `apps/web/` exists, diff against SCREEN-INTENT — do not blindly diff pixels

## Agent workflow — after UI paradigm change

Update when any of: new shared component pattern, layout shift, token change, new/changed route flow, status UX change.

1. Edit **Implementation notes** table above
2. Update [UX-FLOW.md](./UX-FLOW.md) + [SCREEN-INTENT.md](./SCREEN-INTENT.md) + [SCREEN-INTENT-MAP.md](./SCREEN-INTENT-MAP.md)
3. Update [design-tokens.md](./design-tokens.md) if tokens changed
4. Mention doc updates in commit/PR summary

Rule: [.cursor/rules/ui-product-sync.mdc](../.cursor/rules/ui-product-sync.mdc) · Skill: [.cursor/skills/ui-product-sync/SKILL.md](../.cursor/skills/ui-product-sync/SKILL.md)

---

*Last updated: HAC-21 — UX paradigm shift (editable diagnosis, timeline-only forge, vertical roadmap steady state)*
