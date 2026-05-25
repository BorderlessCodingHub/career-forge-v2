# Screen Intent — Career Forge

> **Per-screen must-match for agents.** Non-negotiable UX constraints.  
> Flow narrative: [UX-FLOW.md](./UX-FLOW.md) · Route table: [SCREEN-INTENT-MAP.md](./SCREEN-INTENT-MAP.md)

---

## Global rules

- All user-facing copy: **Portuguese (Brazil)**
- Status enum: `bloqueado | recomendado | em_estudo | validar | aprovado | revisar` — never rename without CHECKPOINT + API
- No gamification (confetti, XP, streaks)
- P0 wow moments must survive: **Forge stream**, **Animation reveal**, **Validation**, **Adaptive roadmap**

---

## 1. Goal Picker — MUST match

| Constraint | Detail |
|------------|--------|
| Headline | *"Para onde você quer ir?"* |
| Subhead | *"Antes de te dar um plano…"* |
| Cards | Backend active; Data / Frontend disabled "Em breve" |
| Motivation | Required in happy path — feeds downstream AI |
| CTA | Single primary action to onboarding |

**Can evolve:** hover states, validation toast, animation library

---

## 2. Onboarding chat — MUST match

| Constraint | Detail |
|------------|--------|
| Feel | Focused diagnostic — **not** open-ended ChatGPT |
| Progress | Step indicator visible (e.g. Passo 2/3) |
| Recap | Goal + motivation from step 1 visible |
| Exit | Transitions to **editable diagnosis** — not forge directly |

**Can evolve:** streaming vs batch API, exact question count (4–6)

---

## 3. Editable diagnosis — MUST match ⭐ NEW

| Constraint | Detail |
|------------|--------|
| Purpose | User **corrects** AI understanding before forge |
| Edit | Each list item editable inline |
| Add | User can add items to fortes / lacunas / recomendação |
| Remove | User can remove items |
| Profile badge | e.g. "Iniciante com base em JavaScript" |
| Evidence callout | Avaliação por evidência — no fake "concluído" |
| CTA | **"Gerar roadmap"** — explicit forge trigger |
| Forbidden | Read-only confirmation with passive "Ver minha trilha" dead-end |

**Can evolve:** drag-reorder, autosave, sidebar vs full page

---

## 4. Live Roadmap Forge — MUST match ⭐ REDESIGNED

| Constraint | Detail |
|------------|--------|
| Layout | **Timeline only** — full width or centered column |
| During stream | **NO skill graph, NO map, NO split panel** |
| Steps | Numbered 1, 2, 3, 4… (or N) **only during generation** |
| Event types | `reasoning_delta`, `artifact_found`, `decision` visual language |
| Feedback | Sequential timeline items — **no generic spinner as primary UX** |
| Header | "Forjando sua trilha personalizada" + elapsed / passos |
| Exit | On `graph_ready` → animation reveal |

**Can evolve:** SSE reconnect, scroll auto-behavior, skip control

**Forbidden:** Right-panel graph skeleton filling during stream (old paradigm)

---

## 5. Animation reveal — MUST match ⭐ REDESIGNED

| Constraint | Detail |
|------------|--------|
| Transition | Stream items **fly into place** on vertical roadmap layout |
| Result | Spine + category nodes materialize left/right |
| Feel | Premium completion — **no confetti** |
| Next | Auto or CTA → `/roadmap` steady state |

**Can evolve:** Framer Motion vs CSS, duration, stagger timing

---

## 6. Vertical roadmap (steady state) — MUST match ⭐ REDESIGNED

| Constraint | Detail |
|------------|--------|
| Layout | Vertical spine, nodes alternating left/right, category headers |
| Reference | [roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) — layout inspiration |
| Personalization | Adaptive skill graph state — not static checklist |
| Node status | Pills + mastery % when known; locked dimmed |
| Mission | Next action visible (MissionBanner or equivalent) |
| AI sidebar | **Optional** — user opens/closes. Explain / Test / Chat |
| Forbidden | Forge streaming view as steady state; step numbers 1–N on nodes |

**Can evolve:** node click → detail panel, graph library, sidebar width

---

## 7. Mastery validation — MUST match

| Constraint | Detail |
|------------|--------|
| Headline | *"Pronto para validar seu aprendizado?"* |
| Subhead | Entrevista antes de liberar próximo tópico |
| Flow | Question card + textarea + submit |
| Result | ScoreRing, status pill, acertou / melhorar / próximo passo |
| Mentor summary | Collapsible optional block |

**Can evolve:** question count (3±), retry copy, wizard vs single page

---

## 8. Adaptive roadmap — MUST match

| Constraint | Detail |
|------------|--------|
| Trigger | Failed validation → node `revisar` |
| Visual | Failed topic amber/pulse; priority bump visible |
| Mission | Banner reflects validation gap |
| Mentor | Contextual plan referencing **specific** failed validation |

**Can evolve:** drawer vs AI sidebar extension (P1 HAC-13)

---

## Verification hooks (Playwright Gate B)

| Screen | `data-testid` |
|--------|---------------|
| Goal picker | `goal-picker` |
| Editable diagnosis | `diagnosis-editable` |
| Forge timeline | `forge-timeline` |
| Vertical roadmap | `vertical-roadmap` |
| Validation score | `validation-score` |

---

*Last updated: HAC-21*
