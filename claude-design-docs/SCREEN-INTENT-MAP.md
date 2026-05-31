# Screen Intent Map — Career Forge

> Route table + quick reference. Must-match detail: [SCREEN-INTENT.md](./SCREEN-INTENT.md) · Flow: [UX-FLOW.md](./UX-FLOW.md)

---

## Demo flow (canonical — HAC-21)

```
/ → /onboarding → /onboarding/edit → /roadmap/forge → /roadmap/forge/complete → /roadmap → /validate/:topic → /roadmap (adaptive)
```

Breadcrumb: **Goal → Diagnosis → Review → Forge → Explore → Validate**

5-min demo: [CHECKPOINT](../docs/CHECKPOINT.md#demo-script-5-min)

---

## Screen reference table

| # | App route | Prototype hash (legacy) | `data-screen` | Wow? | Must match | Can evolve |
|---|-----------|-------------------------|---------------|------|------------|------------|
| 1 | `/` | `goal` | `goal-picker` | — | Headline PT-BR, 3 career cards, motivation textarea, single CTA | Card hover, validation toast |
| 2 | `/onboarding` | `diag` | `diagnostic` | — | Chat layout, 4–6 Q thread, recap of goal | Streaming vs batch API |
| 3 | `/onboarding/edit` | `result` ⚠️ | `diagnosis-editable` | — | **Editable** lists, add/remove, CTA **"Generate roadmap"** | Drag-reorder, autosave |
| 4 | `/roadmap/forge` | `forge` ⚠️ | `forge-stream` | **P0** | **Timeline only**, numbered steps, **no graph during stream** | SSE reconnect, scroll |
| 4b | `/roadmap/forge/complete` | (inline reveal) ⚠️ | `forge-reveal` | **P0** | Items fly into vertical layout | Animation library |
| 5 | `/roadmap` | `roadmap` ⚠️ | `vertical-roadmap` | **P0** | Vertical spine; cards show compact study `x/y` + mint bar when checklist items exist; drawer has full checklist + progress | Node detail panel, sidebar UX |
| 6 | `/validate/:topic` | `validate` | `validation` | **P0** | Interview headline, Q progress, ScoreRing result | Question count (3±) |
| 7 | `/roadmap` | `adaptive` | `adaptive-state` | **P0** | Roadmap diff after fail, mentor/AI context | Drawer vs sidebar |

⚠️ = prototype hash reflects **pre-HAC-21** flow/layout — use [SCREEN-INTENT.md](./SCREEN-INTENT.md) for truth.

---

## Deprecated routes

| Route | Replaced by |
|-------|-------------|
| `/onboarding/result` (read-only confirmation) | `/onboarding/edit` |

---

## Per-screen intent (summary)

Full must-match: [SCREEN-INTENT.md](./SCREEN-INTENT.md)

### 1. Goal Picker (`/`)
Declare dream role + motivation. Prototype: `screens-flow.jsx`

### 2. AI Diagnostic (`/onboarding`)
Short diagnostic chat. Exit → editable diagnosis (not forge). Prototype: `screens-flow.jsx`

### 3. Editable Diagnosis (`/onboarding/edit`) ⭐ NEW
User edits/adds/removes strengths, gaps, recommendation. CTA: **"Generate roadmap"**. Replaces read-only confirmation.

### 4. Live Roadmap Forge (`/roadmap/forge`) ⭐ REDESIGNED
Timeline-only stream, steps 1–N. No graph during generation. Prototype split layout is **legacy**.

### 4b. Animation Reveal (`/roadmap/forge/complete`) ⭐ REDESIGNED
Stream items animate into vertical roadmap positions.

### 5. Vertical Roadmap (`/roadmap`) ⭐ REDESIGNED
Steady state — roadmap.sh-style vertical layout + optional AI sidebar. Reference: [roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png)

**Canvas cards:** When `checklist_total > 0`, `SkillNode` shows compact `ChecklistProgress` (`roadmap-node-{id}-checklist-progress`) — `x/y` + thin mint bar only.

**Artifact topbar:** `artifact-topbar` — track name; right cluster `items-end`; single `h-9` action `mentor-report-link` + `FileText` (no progress ring).

**Page intro:** centered subtitle + optional `trail-progress-ring` below (`getTrailChecklistProgressPct`, item-pooled) + **Study progress** label.

**Node drawer (HAC-63):** Header title + red dismiss **✕**; Escape closes. Description callout when no knowledge gaps. Status/mastery, study progress, collapsible outcomes/refs/tasks (default expanded), optional `open-tutor-drawer`, sticky `validate-node-cta`. Persist via `PATCH /roadmap/nodes/{node_id}/checklist` (adaptive: local-only).

**Canvas spine:** nodes alternate left/right; solid `roadmap-connector-{id}` links each card to spine dot (`border` / `warning` revisar / `accent-mint` selected).

**Loading:** `vertical-spine-skeleton` placeholder spine with connector stubs (no lone text spinner as primary feedback).

### 6. Mentor evidence report (`/report`)
Borderless learning evidence for ambassadors. Entry: artifact topbar **`mentor-report-link`**.

**Validation cards:** human topic title (`formatNodeTitleForDisplay`); score + status; structured **Mentor summary** (gaps / correct answers / next step) — `data-testid="mentor-report-entry-{node_id}"`.

### 7. Mastery Validation (`/validate/:topic`)
Interview + score. Unchanged.

### 8. Adaptive Roadmap (`/roadmap` updated)
Roadmap reacts post-validation. Subtitle + highlighted node on spine; no mission banner on canvas. Mentor via node drawer only. `?adaptive=1` without stored session → silent server fallback.

---

## Status → visual mapping

| Status | Pill color | Roadmap node | User meaning |
|--------|------------|--------------|--------------|
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

Playwright Gate B targets:

- `data-testid="goal-picker"`
- `data-testid="diagnosis-editable"`
- `data-testid="forge-timeline"`
- `data-testid="vertical-roadmap"`
- `data-testid="roadmap-node-{id}-checklist-progress"` (canvas card compact bar)
- `data-testid="artifact-topbar"` · `data-testid="mentor-report-link"`
- `data-testid="vertical-roadmap"` · `data-testid="trail-progress-ring"` (page intro, not topbar)
- `data-testid="roadmap-connector-{id}"` · `data-testid="vertical-spine"`
- `data-testid="mentor-report"` · `data-testid="mentor-report-entry-{node_id}"`
- `data-testid="vertical-spine-skeleton"` · `data-testid="node-drawer"` · `data-testid="node-checklist-progress"` · `data-testid="checklist-non-blocking-copy"`
- `data-testid="checklist-task-{id}"` · `data-testid="checklist-reference-{id}"` · `data-testid="open-tutor-drawer"` · `data-testid="validate-node-cta"` · `data-testid="mentor-report-link"`
- `data-testid="validation-score"`

See [AGENT-DELIVERY.md](../docs/AGENT-DELIVERY.md).

---

*Last updated: 2026-05-30 — `/report` mentor evidence + structured summary testids*
