# PRODUCT SOURCE OF TRUTH — Career Forge

> **Canonical doc for agents.** Read this before any UI work. Update this when the UI paradigm changes.

**Navigation:** [README](./README.md) · [UX-FLOW](./UX-FLOW.md) · [SCREEN-INTENT](./SCREEN-INTENT.md) · [PRODUCT-VISION](./PRODUCT-VISION.md) · [UI-PRINCIPLES](./UI-PRINCIPLES.md) · [BORDERLESS-THEMING](./BORDERLESS-THEMING.md) · [CHECKPOINT](../docs/CHECKPOINT.md)

---

## What this doc is

Single place to resolve conflicts between:

1. **Claude Design prototype** — [`prototype/`](./prototype/) (visual + component reference; **flow may lag** — see UX-FLOW)
2. **Implemented UI** — `apps/frontend/` when it exists (runtime truth for behavior)
3. **Hackathon product goals** — [CHECKPOINT](../docs/CHECKPOINT.md), [handoff context](../docs/handoff_chat_gpt.txt)

Agents compare all three before coding UI. After sessions that change layout, tokens, flows, or component patterns, **update this doc** (and linked docs) so the next agent does not drift.

---

## Canonical UX flow (HAC-21 + HAC-25)

```
Goal → Onboarding pill rounds → Editable diagnosis → [Gerar roadmap] → Forge stream (timeline only) → Animation reveal → Vertical roadmap (artifact mode)
```

**App modes (prototype + target app):**

| Mode | Screens | Chrome |
|------|---------|--------|
| `setup` | Goal, diagnostic, diagnosis edit, forge, validation | Onboarding stepper (01–07) optional/minimal |
| `artifact` | Steady `/roadmap`, adaptive recalibration | Logo + track name only; **no** stepper; **no** fixed progress sidebar |

Full screen-by-screen: [UX-FLOW.md](./UX-FLOW.md) · Must-match: [SCREEN-INTENT.md](./SCREEN-INTENT.md)

---

## Source-of-truth hierarchy

When sources conflict, apply this order **unless** an active Linear issue explicitly overrides (scoped to that issue only):

| Priority | Source | Wins when… | Agent action |
|----------|--------|------------|--------------|
| **1** | **Hackathon goals** — [CHECKPOINT](../docs/CHECKPOINT.md) P0 wow features, demo script, out-of-scope | Prototype or code adds scope, weakens AI-as-motor, or breaks 5-min demo | Cut or defer; do not ship |
| **2** | **Screen intent** — [SCREEN-INTENT.md](./SCREEN-INTENT.md) + [UX-FLOW.md](./UX-FLOW.md) | Prototype detail contradicts wow moment or route purpose | Match intent; prototype is reference not law |
| **3** | **Claude Design prototype** — [`prototype/`](./prototype/), [design-tokens.md](./design-tokens.md) | No implemented UI yet, or implementation diverges without documented reason | Tokens/components from prototype; **flow from UX-FLOW** |
| **4** | **Implemented UI** — `apps/frontend/` | Deliberate evolution documented in **Implementation notes** below | Code wins; update docs same session |
| **5** | **Brief history** — [brief-v1.md](./brief-v1.md) | Prototype already evolved past an old prompt | Prefer UX-FLOW + this doc over brief |

### Tie-breakers

- **Copy (PT-BR):** Prototype microcopy wins unless CHECKPOINT/demo script requires different wording.
- **Tokens:** [design-tokens.md](./design-tokens.md) + [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) win over ad-hoc hex in JSX/CSS. Tailwind theme must map to Borderless tokens (not legacy indigo).
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

## Theming (Borderless — HAC-23)

**Canonical:** [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md)

Career Forge uses **Borderless Community** visual language within the Borderless ecosystem:

| Aspect | Spec |
|--------|------|
| Palette | Deep purple-black bg, purple nodes, cyan/mint progress, logo purple accent |
| Shell | Fixed sidebar + top search bar + full-width canvas |
| Steady state | Code Breakers–style node canvas — **uniform purple nodes** on artifact canvas; status in node drawer |
| Flow | HAC-21 forge → reveal → **HAC-25 artifact mode** (roadmap.sh finished page) |

**Reference images:**

| File | Role |
|------|------|
| [references/borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png) | Shell, sidebar, canvas, nodes, connections |
| [references/borderless-logo-brand.png](./references/borderless-logo-brand.png) | Brand colors (mint + purple) |
| [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) | AI sidebar layout only (secondary) |
| [references/roadmap-sh-reference-full.png](./references/roadmap-sh-reference-full.png) | Full roadmap.sh steady-state layout |
| [references/trail-dashboard-polluted-current.png](./references/trail-dashboard-polluted-current.png) | Anti-pattern — cluttered dashboard (pre HAC-25) |
| [references/forge-screen-current.png](./references/forge-screen-current.png) | Forge split layout (approved) + uniform node target |

Prototype plan: [MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md) · Feedback: [UI-SUGGESTIONS-BACKLOG.md](./UI-SUGGESTIONS-BACKLOG.md)

---

## UI principles (summary)

Full spec: [UI-PRINCIPLES](./UI-PRINCIPLES.md) · Theming: [BORDERLESS-THEMING](./BORDERLESS-THEMING.md)

- **Borderless shell** + **canvas roadmap** (Code Breakers reference) + adaptive skill graph (status, mastery %)
- Dark purple-black aesthetic — tokens in [design-tokens.md](./design-tokens.md)
- Portuguese (Brazil) for all user-facing copy
- Premium dev-tool feel — no LMS chrome, no confetti/gamification
- Hero moments: **Forge timeline stream**, **Animation reveal**, **Validation interview + score**
- Steady state: canvas nodes + **optional** AI sidebar (Explain / Test / Chat)

**Primary layout reference:** [borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png)

---

## Screen map (summary)

Full table: [SCREEN-INTENT-MAP.md](./SCREEN-INTENT-MAP.md) · Must-match: [SCREEN-INTENT.md](./SCREEN-INTENT.md)

| Route | Must match | Can evolve in code |
|-------|------------|-------------------|
| `/` Goal picker | Hero + 3 cards + motivation field | Animation library, form validation UX |
| `/onboarding` | Chat diagnostic, 4–6 Q feel; short negative answers like "Nada." are valid evidence | Streaming vs batch API |
| `/onboarding/edit` | **Editable** fortes/lacunas/prioridades + **"Gerar roadmap"** | HAC-53: view-first, pencil/trash, dnd-kit reorder, refazer diagnóstico |
| `/roadmap/forge` | **Timeline only** — numbered steps, no graph during stream; research rows show formatted summary + official source cards; planner/evaluator artifacts may appear; manual **"Ver roadmap"** CTA after `graph_ready` | SSE wiring, scroll behavior |
| `/roadmap/forge/complete` | Stream items fly into vertical layout | Motion implementation |
| `/roadmap` | **Vertical roadmap** steady state + optional AI sidebar; node drawer shows tasks/references with optional study checklist (non-blocking) + progress bar | Node detail panel, sidebar UX |
| `/validate/:topic` | Interview + ScoreRing result | Voice, timer — out of MVP |
| `/roadmap` (adaptive) | Roadmap state change + mentor/AI context | Drawer vs sidebar |

Prototype entry: [`prototype/index.html`](./prototype/index.html) or [`prototype/README.md`](./prototype/README.md) — run `python3 -m http.server 8765` in `prototype/` → `http://localhost:8765/`

---

## Linked reference files

| File | Role |
|------|------|
| [UX-FLOW.md](./UX-FLOW.md) | Canonical flow + old vs new |
| [SCREEN-INTENT.md](./SCREEN-INTENT.md) | Per-screen must-match |
| [brief-v1.md](./brief-v1.md) | Original Claude Design prompts per screen |
| [design-tokens.md](./design-tokens.md) | Color, type, status pills, spacing (Borderless) |
| [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) | Canonical Borderless visual language |
| [MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md) | HTML prototype evolution phases |
| [UI-SUGGESTIONS-BACKLOG.md](./UI-SUGGESTIONS-BACKLOG.md) | User UI feedback backlog |
| [references/borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png) | Shell + canvas + nodes (primary) |
| [references/borderless-logo-brand.png](./references/borderless-logo-brand.png) | Brand colors |
| [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) | AI sidebar layout (secondary) |
| [prototype/](./prototype/) | Component/token reference (flow may lag) |
| [docs/CHECKPOINT.md](../docs/CHECKPOINT.md) | Stack, wow features, demo script, scope |
| [docs/stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md) | Forge SSE + LangGraph spec |

---

## Implementation notes (living)

*Update this section when `apps/frontend/` diverges from docs on purpose.*

| Topic | Docs (HAC-21) | Prototype (legacy) | Implemented | Decision | Date |
|-------|-----------------|-------------------|-------------|----------|------|
| Diagnosis answer validation | Pill rounds accept meaningful short answers | Prototype did not define min length | `MIN_ANSWER_LENGTH=1`; disabled button has visible disabled state | **Code + backend contract win** — "Nada." is valid evidence | 2026-05-27 |
| Post-diagnosis | Editable `/onboarding/edit` | Read-only `/onboarding/result` | HAC-53 shipped — view-first edit, dnd-kit priorities, sessionStorage | **Docs + code aligned** | HAC-53 |
| Forge during stream | Timeline only, no graph | Split timeline + graph skeleton | Implemented | **Docs win** — timeline-only wow | HAC-18 |
| Steady state | Vertical roadmap + optional AI sidebar | Skill graph dashboard | Implemented (HAC-9) | **Docs win** — roadmap.sh layout | HAC-9 |
| Reveal | Items fly into vertical layout | Graph panel reveal | Implemented | **Docs win** | HAC-18 |
| Monorepo UI | Full flow per UX-FLOW | Old hash routes in HTML | Mostly implemented | HAC-52 API done (`/diagnosis/confirm`, forge loads profile); **HAC-57** wires confirm button | HAC-52 |
| Forge research + evaluation | Timeline-only stream with `artifact_found` rows | Mock artifacts without live sources | HAC-54 — OpenAI native `web_search` citations, planner artifact, evaluator verdict, paced instant steps, then manual **Ver roadmap** CTA | **Code + docs aligned** — no third-party search adapter | HAC-54 |
| Generated roadmap details | Drawer can show references/outcomes | Prototype lacks generated StudyPlan fields | HAC-55 — dynamic nodes reload from backend with `tasks[]` and `references[]` | **Code wins** — richer graph data | HAC-55 |
| Drawer study checklist | Optional read/practice tracking | Prototype has no per-item progress | **HAC-63** — `NodeDrawer`: checkboxes (`checklist-task-{id}`, `checklist-reference-{id}`), progress block (`node-checklist-progress`, `checklist-non-blocking-copy`), mint bar; `PATCH /roadmap/nodes/{node_id}/checklist` persists `checklist_progress` JSONB per user+node; adaptive `?adaptive=1` updates local state only | **Code wins** — study aid only; `validate-node-cta` unchanged | 2026-05-28 |
| Forge events | Mock `FORGE_SCRIPT` | SSE from FastAPI (HAC-18) | SSE wired | Map SSE to timeline UI only | HAC-18 |
| Prod persistence | Postgres diagnosis + graph runs | InMemory stores | HAC-58 — auto postgres when ENV=production | **Code wins** | HAC-58 |
| Deploy badge (global footer) | Not in prototype | N/A | Fixed bottom strip on all routes — `DeployBadge` in root layout; `local dev` when `NEXT_PUBLIC_BUILD_*` unset; prod shows `deploy {sha} · {time}` from CI; health dot polls `GET /health` | **Code wins** — operational debug chrome, not pitch UX; does not replace demo script checks | 2026-05-27 |

---

## Agent workflow — before UI work

1. Read this file → [UX-FLOW](./UX-FLOW.md) → [SCREEN-INTENT](./SCREEN-INTENT.md) → [BORDERLESS-THEMING](./BORDERLESS-THEMING.md) → [UI-PRINCIPLES](./UI-PRINCIPLES.md)
2. Open [references/borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png) for steady-state shell + canvas
3. Open prototype via [`prototype/README.md`](./prototype/README.md) (`http://localhost:8765/`) for tokens/components
4. Read [CHECKPOINT](../docs/CHECKPOINT.md) for P0 scope
5. If `apps/frontend/` exists, diff against SCREEN-INTENT — do not blindly diff pixels

## Agent workflow — after UI paradigm change

Update when any of: new shared component pattern, layout shift, token change, new/changed route flow, status UX change.

1. Edit **Implementation notes** table above
2. Update [UX-FLOW.md](./UX-FLOW.md) + [SCREEN-INTENT.md](./SCREEN-INTENT.md) + [SCREEN-INTENT-MAP.md](./SCREEN-INTENT-MAP.md)
3. Update [design-tokens.md](./design-tokens.md) + [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) if tokens/theming changed
4. Mention doc updates in commit/PR summary

Rule: [.cursor/rules/ui-product-sync.mdc](../.cursor/rules/ui-product-sync.mdc) · Skill: [.cursor/skills/ui-product-sync/SKILL.md](../.cursor/skills/ui-product-sync/SKILL.md)

---

*Last updated: 2026-05-27 — deploy badge footer (build SHA + API health)*
