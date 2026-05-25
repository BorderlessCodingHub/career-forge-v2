# Screen Intent Map — Career OS

> Route-by-route intent for agents. Prototype: [`prototype/app.jsx`](./prototype/app.jsx) · Hierarchy: [PRODUCT-SOURCE-OF-TRUTH](./PRODUCT-SOURCE-OF-TRUTH.md)

---

## Demo flow (canonical order)

```
/ → /onboarding → /onboarding/result → /roadmap/forge → /roadmap/forge/complete → /roadmap → /validate/:topic → /roadmap (adaptive)
```

Breadcrumb mental: **Objetivo → Diagnóstico → Trilha → Validação**

5-min demo script: [CHECKPOINT](../docs/CHECKPOINT.md#demo-script-5-min)

---

## Screen reference table

| # | App route | Prototype hash | `data-screen` | Wow? | Must match | Can evolve |
|---|-----------|----------------|---------------|------|------------|------------|
| 1 | `/` | `goal` | `goal-picker` | — | Headline PT-BR, 3 career cards, motivation textarea, single CTA | Card hover, validation toast |
| 2 | `/onboarding` | `diag` | `diagnostic` | — | Chat layout, 4–6 Q thread visible, recap of goal | Streaming tokens vs instant |
| 2b | `/onboarding/result` | `result` | `diagnosis-result` | — | 3 blocks: fortes / lacunas / recomendação | Sidebar vs full page |
| 3 | `/roadmap/forge` | `forge` | `forge-stream` | **P0** | Split view, timeline types, graph skeleton filling | Scroll auto-behavior, SSE reconnect |
| 3b | `/roadmap/forge/complete` | (inline reveal) | `forge-reveal` | **P0** | Full graph + MissionBanner + CTA explorar | Animation library |
| 4 | `/roadmap` | `roadmap` | `skill-graph` | **P0** | Graph hero, status colors, sidebar summary, node detail | Graph rendering tech |
| 5 | `/validate/:topic` | `validate` | `validation` | **P0** | Interview headline, Q progress, result ScoreRing | Number of questions (3±) |
| 6 | `/roadmap` | `adaptive` | `adaptive-state` | **P0** | Graph diff after fail, mentor drawer with contextual plan | Drawer width, chat UX |

---

## Per-screen intent

### 1. Goal Picker (`/`)

**User job:** Declare dream role + motivation.

**Must match**
- Copy: *"Para onde você quer ir?"* / *"Antes de te dar um plano…"*
- Backend Developer active; Data / Frontend disabled "Em breve"
- Motivation field feeds downstream AI — not optional in happy path

**Can evolve**
- Form validation, keyboard nav, loading on submit

**Prototype:** `screens-flow.jsx` · Prompt: [brief-v1.md § Tela 1](./brief-v1.md)

---

### 2. AI Diagnostic (`/onboarding`)

**User job:** Answer short free-text questions so IA maps known vs gaps.

**Must match**
- Feels like focused diagnostic — not open-ended ChatGPT
- Progress indicator (Step 2/3 or equivalent)
- Recap card: goal + motivation from step 1

**Can evolve**
- Exact question count (4–6)
- API shape for messages

**Prototype:** `screens-flow.jsx` · [brief-v1.md § Tela 2](./brief-v1.md)

---

### 2b. Diagnosis Result (`/onboarding/result`)

**User job:** See structured output before forge — trust the system understood them.

**Must match**
- Sections: pontos fortes (green), lacunas (amber), recomendação
- Profile badge (e.g. "Iniciante com base em JavaScript")
- CTA toward forge / trilha

**Can evolve**
- Brief interstitial vs persistent sidebar during forge

**Prototype:** `screens-flow.jsx` · [brief-v1.md § Tela 4](./brief-v1.md)

---

### 3. Live Roadmap Forge (`/roadmap/forge`) ⭐

**User job:** Witness AI building *their* trail — emotional peak #1.

**Must match**
- Left: live timeline — `reasoning_delta`, `artifact_found`, `decision` visual language
- Right: graph skeleton → partial nodes → lines
- Header: progress ("Construindo skill graph…")
- **No** full polished graph until reveal step

**Can evolve**
- Mock `FORGE_SCRIPT` → real SSE ([stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md))
- Iteration count display

**Prototype:** `screens-forge.jsx` · [brief-v1.md § Tela 3](./brief-v1.md)

---

### 3b. Graph Reveal (`/roadmap/forge/complete`) ⭐

**User job:** Closure — "minha trilha existe."

**Must match**
- All nodes solid with status + mastery %
- MissionBanner: concrete next mission (e.g. HTTP básico)
- Premium dev-tool celebration — **no confetti**

**Can evolve**
- Transition choreography (Framer Motion, CSS)

**Prototype:** `screens-forge.jsx` · [brief-v1.md § Tela 3b](./brief-v1.md)

---

### 4. Skill Graph Dashboard (`/roadmap`) ⭐

**User job:** Orient daily — what's next, what's blocked, what's proven.

**Must match**
- MissionBanner top
- ~7 nodes with dependency edges (Backend Beginner MVP)
- Sidebar: progress fraction, recent evidence, mentor CTA
- Node click → detail panel with outcomes + "Validar com IA" when unlocked

**Can evolve**
- Slide-over vs modal for node detail
- React Flow vs custom SVG — layout should match prototype feel

**Prototype:** `screens-dashboard.jsx`, `skill-graph.jsx` · [brief-v1.md § Tela 5](./brief-v1.md)

---

### 5. Mastery Validation (`/validate/:topic`) ⭐

**User job:** Prove learning — emotional peak #2.

**Must match**
- Headline: *"Pronto para validar seu aprendizado?"*
- Subhead: entrevista antes de liberar próximo tópico
- Question card + textarea + submit
- Result: ScoreRing, status pill, acertou / melhorar / próximo passo
- Collapsible mentor_summary

**Can evolve**
- Single-page vs step wizard for questions
- Retry flow copy

**Prototype:** `screens-dashboard.jsx` (validation section) · [brief-v1.md § Tela 6](./brief-v1.md)

---

### 6. Adaptive + Mentor (`/roadmap` updated)

**User job:** See system react — trilha is alive.

**Must match**
- REST (or failed topic) → `revisar` amber
- HTTP bumped to top priority / pulse
- MissionBanner reflects validation gap
- Mentor drawer: 40-min plan referencing **specific** failed validation

**Can evolve**
- Mentor as drawer vs panel (P1 HAC-13)

**Prototype:** `screens-dashboard.jsx` adaptive mode · [brief-v1.md § Tela 7](./brief-v1.md)

---

## Status → visual mapping

| Status | Pill color | Graph node | User meaning |
|--------|------------|------------|--------------|
| `bloqueado` | locked / dim | Gray, no CTA | Prerequisite missing |
| `recomendado` | accent | Highlight | Study this now |
| `em_estudo` | secondary | Normal | In progress |
| `validar` | evidence | Ready ring | Ready for interview |
| `aprovado` | success | Check + % | Mastery proven |
| `revisar` | warning | Pulse/amber | Failed validation |

Tokens: [design-tokens.md](./design-tokens.md)

---

## Routes not in MVP UI

Do not add screens without Linear issue + CHECKPOINT update:

- Auth / login
- Admin / turma dashboard
- Multi-track picker (beyond disabled cards)
- Settings / change goal (post-MVP)

---

## Verification hooks

Playwright Gate B targets (extend as UI ships):

- `data-testid="goal-picker"`
- `data-testid="forge-timeline"`
- `data-testid="skill-graph"`
- `data-testid="validation-score"`

See [AGENT-DELIVERY.md](../docs/AGENT-DELIVERY.md).
