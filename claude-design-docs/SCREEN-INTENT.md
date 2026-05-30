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
| Subhead | Optional — keep minimal; no long explanatory paragraph required |
| Cards | Backend active; Data / Frontend disabled "Em breve" |
| Layout | **Minimal** — compact row cards, no heavy chrome (icons, meta badges, footer notes) |
| Motivation | Required in happy path — feeds downstream AI |
| CTA | Single primary action to onboarding |

**Can evolve:** hover states, validation toast, animation library

---

## 2. Onboarding diagnostic — MUST match

| Constraint | Detail |
|------------|--------|
| Feel | Focused diagnostic — **not** open-ended ChatGPT |
| Layout | **Pill/balloon rounds** — multiple questions shown together per round |
| Rounds | 3 batches: seniority/context → stack/domain → gaps (Git, HTTP, APIs, DB) |
| Input | Each pill has its own textarea — **not** one-at-a-time chat bubbles; explicit short negative answers like "Nada." are valid signal |
| Progress | Step indicator + round counter (e.g. Rodada 2/3) |
| Recap | Goal + motivation from step 1 visible in sidebar |
| Exit | Transitions to **editable diagnosis** — not forge directly |

**Can evolve:** streaming vs batch API, exact question count (4–6 total)

**Forbidden:** Linear chat bubble UX (one question → one reply → next question)

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
| Event types | `reasoning_delta`, `artifact_found`, `decision` visual language; `artifact_found` may include formatted summaries, official source cards, planner/evaluator verdicts |
| Feedback | Sequential timeline items — **no generic spinner as primary UX** |
| Header | "Forjando sua trilha personalizada" + elapsed / passos |
| Exit | On `graph_ready` → show manual **"Ver roadmap"** CTA → animation reveal |

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

## 6. Vertical roadmap (steady state) — MUST match ⭐ ARTIFACT MODE (HAC-25)

| Constraint | Detail |
|------------|--------|
| App mode | **`artifact`** — finished personalized roadmap.sh page; distinct from **`setup`** (onboarding + forge) |
| Layout | Full-width vertical spine; nodes alternating left/right; category headers |
| Reference | [roadmap-sh-reference-full.png](./references/roadmap-sh-reference-full.png) · [roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) |
| Chrome | **No** onboarding stepper (01 Objetivo … 07 Adaptação); **no** fixed progress/evidence/mentor sidebar |
| Top bar | Career Forge logo + **Sua trilha** track name; right cluster **`items-end`** — **`mentor-report-link`** action bottom-aligned with track title line; same `topbarActionClass` (`h-9`); relatório = `h-7` icon slot + `FileText` + label; **no** progress ring in topbar; mentor via node drawer only |
| Page intro | Subtitle/hint + optional centered **`trail-progress-ring`** below subtitle (`getTrailChecklistProgressPct` — item-pooled checklist %, not mastery %, not topic-average) + **Progresso de estudo** label — **no** duplicate track `<h1>` on canvas |
| Canvas nodes | **Uniform** Borderless purple cards — compact **study** progress (`x/y` + mint bar) when checklist items exist; **mastery %** and status detail stay in **node drawer** only |
| Interaction | **Click node** → right drawer: title, red **✕** dismiss, Escape to close, status/mastery, study progress, description callout when no gaps, collapsible outcomes/refs/tasks (default expanded), optional tutor row, sticky CTA **Mock interview — validar mastery** |
| Personalization | Graph state still adaptive (backend recalibrates) — visible in drawer, not canvas pollution |
| Forbidden | Forge streaming as steady state; MissionBanner hero on artifact canvas; status-colored node grid |

**Can evolve:** drawer width, reference API, full AI tutor panel vs mini chat

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
| Mission | Gap context on validation result + highlighted node on spine — **no** mission banner on artifact canvas |
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

*Last updated: HAC-25 — artifact mode steady state; HAC-26 backlog audit*
