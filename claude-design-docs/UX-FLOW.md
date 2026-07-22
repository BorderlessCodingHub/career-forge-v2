# UX Flow — Career Forge

> **Canonical flow (HAC-21).** Screen-by-screen narrative with old vs new paradigm.  
> Must-match constraints: [SCREEN-INTENT.md](./SCREEN-INTENT.md) · Hierarchy: [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md)

---

## Flow summary (source of truth)

```
Goal → Onboarding pill rounds → Editable diagnosis → [Generate roadmap] → Forge stream (timeline only) → Animation reveal → Vertical roadmap (artifact mode)
```

**Mental breadcrumb:** Goal → Diagnosis → Review diagnosis → Forge roadmap → Explore roadmap

5-min demo: [CHECKPOINT](../docs/CHECKPOINT.md#demo-script-5-min)

### Global operational chrome (all routes)

Fixed bottom **deploy badge** on every screen (not in prototype): short git SHA + build time in production (`NEXT_PUBLIC_BUILD_*` from CI); `local dev` when unset; colored dot from live `GET /health`. **`z-auto`** so node/mentor drawers (`z-50`) are never covered by the footer. Low-contrast, does not replace pitch demo checks. See [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md) Implementation notes · [DEPLOY-VPS.md](../docs/engineering/DEPLOY-VPS.md).

---

## Paradigm shift (old → new)

| Aspect | Old (pre HAC-21) | New (HAC-21+) |
|--------|------------------|---------------|
| Post-chat diagnosis | Read-only confirmation screen (`/onboarding/result`) — CTA "View my roadmap" | **Editable diagnosis** — user edits/adds/removes items, CTA **"Generate roadmap"** |
| Entry into the forge | Auto-jump or passive CTA after confirmation | **Explicit** — only after "Generate roadmap" |
| Forge during stream | Split 40/60: timeline + skill graph skeleton filling up | **Timeline only** — numbered steps 1, 2, 3, 4… (reasoning stream). **No graph visible** |
| End of the forge | Inline reveal with full graph + MissionBanner | **Animation** — each phrase/item of the stream **flies into place** in the vertical layout |
| Steady state after the forge | Skill graph dashboard (connected nodes, fixed sidebar) | **`artifact` mode** — full-width vertical roadmap in [roadmap.sh](https://roadmap.sh) style; cards show compact study `x/y` + mint bar when there are items; **click node → drawer** (full checklist, study progress, Ask AI, validate mastery); no stepper or progress sidebar |
| Step numbering | Implicit in the timeline | **1–N only during generation** — does not appear in the steady state |
| App modes | Single chrome | **`setup`** (goal → forge) vs **`artifact`** (finished roadmap) |
| AI in the dashboard | Contextual mentor drawer (P1) | **Ask AI** in the node drawer (roadmap.sh tutor style); full mentor drawer = optional P1 |

---

## Screen-by-screen

### 1. Goal Picker (`/`)

**Unchanged.** The user declares their dream profession + motivation.

| | |
|---|---|
| **Old** | Hero + 3–4 hackathon career cards + motivation textarea |
| **New** | Hero + **4** v2 LLM track cards (`rag-engineer`, `agent-engineer`, `llm-evals`, `fine-tuning`) + motivation; default `rag-engineer` |
| **Route** | `/` · `data-screen="goal-picker"` |

---

### 2. Onboarding diagnostic (`/onboarding`)

**Redesigned (HAC-24).** Pill/balloon rounds — 3 batches, 2 questions per round; not linear chat bubbles.

Short explicit negative answers (for example, **"Nothing."**) are valid evidence for the Judge and must not block "Next round".

| | |
|---|---|
| **Old** | Linear chat bubbles — one Q at a time |
| **New** | Pill rounds → generates diagnosis → **editable diagnosis** (not a passive confirmation) |
| **Route** | `/onboarding` · `data-screen="diagnostic"` |

---

### 3. Editable diagnosis (`/onboarding/edit`) ⭐ NEW

**Replaces** read-only diagnosis confirmation screen.

**User job:** Review and **correct** what the AI understood — feel in control before forging the roadmap.

| | |
|---|---|
| **Old** | `/onboarding/result` — 3 read-only blocks (strengths / gaps / recommendation), CTA "View my roadmap" |
| **New** | **View-first** editable lists: edit/delete icons per item, add (+), **drag-and-drop** on priorities (dnd-kit). CTA **"Generate roadmap"** + **"Redo diagnosis"** |
| **Why** | The confirmation screen was a dead-end — no feedback, no agency |
| **Route** | `/onboarding/edit` · `data-testid="editable-diagnosis"` |
| **Shipped** | HAC-53 — view/edit modes per item; strengths/gaps editable; priorities reorderable |
| **On confirm (target)** | `POST /diagnosis/confirm` persists the profile in Postgres → `POST /forge` (202 + run_id) → SSE. **API:** HAC-52 ✅ · **FE wire:** HAC-57 pending |

**Sections (editable lists):**
- Strengths
- Gaps
- Recommendation / 1st mission

---

### 4. Live Roadmap Forge (`/roadmap/forge`) ⭐ REDESIGNED

**User job:** Watch the AI **think** — emotional peak #1.

| | |
|---|---|
| **Old** | Split view: timeline on the left + skill graph skeleton on the right filling up with `node_updated` |
| **New** | **Full-width streaming timeline only.** Numbered steps (1, 2, 3, 4…). Types: `reasoning_delta`, `artifact_found`, `decision`. `artifact_found` may show a formatted summary + official sources. **No graph/map during the stream** |
| **Route** | `/roadmap/forge` · `data-screen="forge-stream"` |

**During generation:**
- Header: "Forging your personalized roadmap"
- Counter: elapsed, steps completed
- Instant steps have a short pause (~1.5s) to keep the feeling of "the AI thinking" without inflating real latency.
- Live research: formatted summary + official source cards when `research_enrich` runs
- Planner/evaluator: artifacts show plan creation and the `ship|revise` verdict; when there is a revise, the AI applies feedback before `graph_ready`.
- Cursor/stream tail active until `graph_ready`
- After `graph_ready`, keep the timeline on screen and show a manual **"View roadmap"** CTA to ease debugging and give the user control.

**NOT during generation:**
- Skill graph preview
- Split panel with a map
- Permanent numbering on the nodes (only in the timeline)

---

### 5. Animation reveal (`/roadmap/forge/complete`) ⭐ REDESIGNED

**User job:** Closure — "my roadmap exists" — a magical transition to the plan.

| | |
|---|---|
| **Old** | Full graph appears in the right panel; MissionBanner; explore CTA |
| **New** | Each item/phrase of the stream **animates flying** into position on the **vertical roadmap layout**. Spine + left/right nodes materialize. No confetti — premium dev-tool |
| **Route** | `/roadmap/forge/complete` · `data-screen="forge-reveal"` |

After the animation → navigates to steady state (`/roadmap`).

---

### 6. Vertical roadmap — steady state (`/roadmap`) ⭐ ARTIFACT MODE (HAC-25)

**User job:** Explore the **final artifact** — a personalized roadmap like a roadmap.sh page, not a setup screen.

| | |
|---|---|
| **Old** | Stepper 01–07 + progress/evidence/mentor sidebar + status-colored nodes |
| **New** | **`artifact` mode:** minimal top bar (logo + roadmap); full-width canvas; **uniform** nodes (Borderless purple); **click → right drawer** with description, practical tasks, references, Ask AI, validate |
| **Route** | `/roadmap` · `data-screen="vertical-roadmap"` · `data-mode="artifact"` |

**References:** [roadmap-sh-reference-full.png](./references/roadmap-sh-reference-full.png) · [trail-dashboard-polluted-current.png](./references/trail-dashboard-polluted-current.png) (anti-pattern)

**Career Forge difference:** Adaptive roadmap — status/mastery appear in the **node drawer**, not polluting the canvas.

**Canvas cards:** when there are `tasks[]` / `references[]`, a compact mint bar + `x/y` fraction on the card (no disclaimer).

**Spine connectors:** a solid horizontal line (`roadmap-connector-{id}`) links each card to the central dot — `border` by default, `warning` when revisar, `accent-mint` when selected.

**Artifact topbar (`/roadmap`):**
- Roadmap name only in the topbar (`Sua trilha`) — page without a duplicate `<h1>`
- **`mentor-report-link`** in the topbar (`FileText` + label) — no progress ring in the topbar

**Roadmap intro (canvas, below the subtitle):**
- Compact **`trail-progress-ring`** centered — % of checklist items completed (not mastery %); hidden when there are no items
- **Study progress** label below the ring
- `getTrailChecklistProgressPct` feeds the ring — same math as `getChecklistProgress` per topic, summing completed/total in a pool (e.g. 11+9+5=25 items; not an average of % per topic)

**Mentor report (`/report`):** accessible via **`mentor-report-link`** in the topbar — human titles per topic; structured summary (gaps, correct answers, next step) per validation.

**Node drawer:**
- Title in the header + red **✕** (`aria-label="Fechar detalhes"`) + **Escape** to close
- **Description** callout in the drawer when there are no knowledge gaps; a gaps block replaces the callout after a failed validation
- Collapsible sections — **Expected outcomes**, **Practical tasks**, and **References** open by default (user can collapse); fixed validate CTA in the footer
- **Practical tasks** section when the graph comes from `StudyPlan` — checkbox per item (optional, does not block mastery)
- **References** section (real links when they come from web search) — mark as read
- **Study progress** bar (`x/y` completed) when there are items; copy makes clear this does not replace AI validation
- **Chapter tutor** (`open-tutor-drawer`) — optional technical Q&A; no inline mentor chat in the drawer
- CTA **Mock interview — validate mastery** (real proof of learning)

---

### 7. Mastery validation (`/validate/:topic`)

**Unchanged** in flow position. Emotional peak #2.

| | |
|---|---|
| **Old** | Interview + ScoreRing |
| **New** | Same |
| **Route** | `/validate/:topic` · `data-screen="validation"` |

---

### 8. Adaptive roadmap (`/roadmap` updated)

**Unchanged intent.** The roadmap reacts after a failed validation.

| | |
|---|---|
| **Old** | Graph diff + mentor drawer |
| **New** | Vertical roadmap updates nodes/status; adaptive signal = subtitle + spine highlight + node drawer (no `MissionBanner` on the canvas); `?adaptive=1` without a session → silent fallback to the server roadmap |
| **Route** | `/roadmap` · `data-screen="adaptive-state"` |

---

## Routes removed / deprecated

| Route | Status |
|-------|--------|
| `/onboarding/result` (read-only confirmation) | **Removed** — replaced by `/onboarding/edit` |

---

## Prototype drift

| Area | Status |
|------|--------|
| Artifact steady state (`#roadmap`) | ✅ HAC-25 — setup vs artifact modes, click-to-drawer |
| Forge uniform nodes | ✅ HAC-25 |
| Editable diagnosis screen | ⬜ Still hash `#result` placeholder |
| Forge timeline-only (no graph during stream) | ⬜ Prototype keeps split forge layout (user approved layout HAC-25) |

Implementation target: this doc + [SCREEN-INTENT.md](./SCREEN-INTENT.md).

---

*Last updated: 2026-05-28 — artifact topbar chrome, trail study summary, drawer accordions*
