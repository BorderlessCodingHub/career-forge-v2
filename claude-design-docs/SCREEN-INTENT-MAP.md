# Screen Intent Map — Career Forge

> Route table + quick reference. Must-match detail: [SCREEN-INTENT.md](./SCREEN-INTENT.md) · Flow: [UX-FLOW.md](./UX-FLOW.md)

---

## Demo flow (canonical — HAC-21)

```
/ → /onboarding → /onboarding/edit → /forge → /forge/complete → /roadmap → /validate/:topic → /roadmap (adaptive)

Recovery (CAR-27/29): / (Continue|View all|New|Forge again) · /forges · /share/:token · /resume/:token (conflict chooser)
```

Breadcrumb: **Goal → Diagnosis → Review → Forge → Explore → Validate** · Recovery: **Continue / forges / share / resume / re-forge**

5-min demo: [CHECKPOINT](../docs/CHECKPOINT.md#demo-script-5-min)

---

## Screen reference table

| # | App route | Prototype hash (legacy) | `data-screen` | Wow? | Must match | Can evolve |
|---|-----------|-------------------------|---------------|------|------------|------------|
| 0 | `/welcome` | `marketing` | `marketing-welcome` | — | EN marketing: BrandMark + Start→`/`; hero diagnose/forge/validate; FAQ ×3; lean motion (CAR-38); no pricing/email | pt-BR CAR-37 |
| 0p | `/welcome/plg` | — | `marketing-welcome-plg` | — | EN product-led; forge HTML mock in hero; before/during/after; dark tokens; not linked from `/welcome` | Visual polish |
| 1 | `/` | `goal` | `goal-picker` / `landing-recovery` | — | Headline EN, **4** LLM track cards (`rag-engineer` default), motivation textarea, single CTA; if ≥1 artifact → Continue / View all / New forge; if diagnosis → Forge again from last diagnosis | Card hover, validation toast |
| 1b | `/forges` | — | `forges-list` | — | Scan & open: Open + Rename visible; share/resume/revoke in ⋯; untitled shows goal_id; optional re-forge CTA | Visual polish |
| 1c | `/share/[token]` | — | `share-readonly` | — | Read-only roadmap; no session adopt | Visual polish |
| 1d | `/resume/[token]` | — | `resume-consume` | — | Conflict chooser when local forges ≠ owner; else adopt; fail on reuse/expiry | Copy polish |
| 2 | `/onboarding` | `diag` | `diagnostic` | — | Chat layout, 4–6 Q thread, recap of goal | Streaming vs batch API |
| 3 | `/onboarding/edit` | `result` ⚠️ | `diagnosis-editable` | — | **Editable** lists, add/remove, CTA **"Generate roadmap"**; also profile-hydrate entry | Drag-reorder, autosave |
| 4 | `/forge` | `forge` ⚠️ | `forge-stream` | **P0** | **Timeline only**, numbered steps, **no graph during stream** | SSE reconnect, scroll |
| 4b | `/forge/complete` | (inline reveal) ⚠️ | `forge-reveal` | **P0** | Items fly into vertical layout; resume copy-once; optional email store | Animation library |
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
**CAR-27/29:** `LandingRecoveryGate` — if ≥1 forge artifact → Continue / View all / New forge (+ optional Forge again); if zero artifacts but saved diagnosis → Welcome back / Forge again / New from scratch; else GoalPicker (`landing-recovery`).

### 1b. Forges list (`/forges`) — CAR-31
Scan & open hierarchy: **Open** + **Rename** visible; Copy share / Copy resume / Revoke share in page-local **⋯**; untitled default titles display `goal_id`; optional re-forge from profile.

### 1c. Share (`/share/[token]`)
Read-only shared roadmap. Fetches `GET /public/share/{token}` — no session adopt.

### 1d. Resume (`/resume/[token]`)
Consume resume token; conflict chooser when local forges ≠ owner; else `adoptSession` → `/roadmap`. Fail clearly on reuse/expiry.

### 2. AI Diagnostic (`/onboarding`)
Short diagnostic chat. Exit → editable diagnosis (not forge). Prototype: `screens-flow.jsx`

### 3. Editable Diagnosis (`/onboarding/edit`) ⭐ NEW
User edits/adds/removes strengths, gaps, recommendation. CTA: **"Generate roadmap"**. Also entry after CAR-29 profile hydrate. Replaces read-only confirmation.

### 4. Live Roadmap Forge (`/forge`) ⭐ REDESIGNED
Timeline-only stream, steps 1–N. No graph during generation. Prototype split layout is **legacy**.

### 4b. Animation Reveal (`/forge/complete`) ⭐ REDESIGNED
Stream items animate into vertical roadmap positions. Resume link copy-once; optional email store (no send).

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

- Auth / login / Borderless issuer (CAR-28)
- Email **send** / SMTP (CAR-28 — store-only is CAR-29)
- Admin / turma dashboard
- Multi-track picker (beyond disabled cards)
- Settings / change goal (post-MVP)
- Mid-flight diagnosis interview resume

---

## Verification hooks

Playwright Gate B targets:

- `data-testid="goal-picker"`
- `data-testid="landing-continue"` · `landing-view-all` · `landing-new-forge` · `landing-reforge-profile` · `landing-recovery-fallback`
- `data-testid="forge-row-{public_id}"` · `forge-open-{id}` · `forge-rename-{id}` · `forge-overflow-{id}` · `forge-title-input-{id}` · `forge-title-save-{id}` · `forge-share-{id}` · `forge-revoke-{id}` · `forge-resume-{id}` · `forges-reforge-profile`
- `data-testid="share-node-list"` · `share-error`
- `data-testid="resume-working"` · `resume-conflict` · `resume-keep-local` · `resume-switch` · `resume-error` · `resume-home`
- `data-testid="forge-resume-copy"` · `forge-resume-copy-btn`
- `data-testid="forge-email-store"` · `forge-email-input` · `forge-email-save` · `forge-email-error`
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

*Last updated: 2026-08-01 — CAR-29 ui-product-sync pass: empty+diagnosis landing + rename title testids*
