# UX Flow — Career Forge

> **Canonical flow (HAC-21).** Screen-by-screen narrative with old vs new paradigm.  
> Must-match constraints: [SCREEN-INTENT.md](./SCREEN-INTENT.md) · Hierarchy: [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md)

---

## Flow summary (source of truth)

```
[/welcome marketing — optional] → Goal → Onboarding pill rounds → Editable diagnosis → [Generate roadmap] → Forge stream (timeline only) → Animation reveal → Vertical roadmap (artifact mode)

Return visit (CAR-27/29): if ≥1 forge artifact → Continue last / View all (/forges) / New forge; if saved diagnosis → Forge again from last diagnosis
Deep-links: /share/{token} (read-only) · /resume/{token} (adopt owner session, single-use; conflict chooser when local forges ≠ owner) · /reference?node=&item= (one Node Reference)
Marketing: /welcome (CAR-56 Premium B) — CTA Start diagnosis → `/` product; pricing/apply scenery; no auto-redirect from `/`. Exploration (direct URL only): `/welcome/plg`. Bake-off A (CAR-41, `noindex`): `/welcome/premium-a`. Legacy `/welcome/premium-b` redirects → `/welcome`.

Operator (separate identity): /operator → Operator OTP → Access | Content desk rooms. Desks outside the seat grant are hidden; no learner or Mentor chrome.
```

**Mental breadcrumb:** (Welcome) → Goal → Diagnosis → Review diagnosis → Forge roadmap → Explore roadmap · Recovery: Continue / forges / share / resume / re-forge from profile

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
| Return visit / recovery | Fresh GoalPicker every load; lost session if localStorage cleared | **CAR-27+29:** landing gate when ≥1 artifact; rich `/forges` (rename/revoke); share + resume; resume **conflict chooser**; optional email store; re-forge from persisted diagnosis |

---

## Screen-by-screen

### 0d. Operator console (`/operator`) — CAR-76 / CAR-78 / CAR-79

Independent workspace on the same Next app and Labs origin. An HttpOnly, path-scoped
Operator session gates the route; learner sessions never open it.

| | |
|---|---|
| **Entry** | Separate Operator email OTP (`data-screen="operator-login"`) |
| **Shell** | Operator lockup, role-filtered desk tabs **Access \| Content**, role-agnostic seat email list, sign out |
| **Access room** | Read-only monthly cost strip → learner email lookup → Access card. Card exposes effective Membership, BASE/PSP override (or clear to Borderless), billing entitlement, Stripe-active read-only lock, and per-learner audit |
| **Content room** | Searchable 40-ID catalog inventory; inline title/URL/published annotations; read-only git body status; publishing disabled until `data/canonical/{skill_id}.md` exists |
| **Route** | `/operator` under `basePath=/career-forge` · `data-screen="operator-console"` |
| **Forbidden** | Learner product chrome, Mentor chrome, Welcome scenery, third Cost desk, role labels in seat list, impersonation |

---

### 1. Goal Picker (`/`)

The user declares their dream profession + motivation. **CAR-27/29:** returning users with ≥1 `forge_artifact` (or a saved diagnosis) see a recovery gate first.

| | |
|---|---|
| **Old** | Hero + 3–4 hackathon career cards + motivation textarea |
| **New** | Hero + **4** v2 LLM track cards (`rag-engineer`, `agent-engineer`, `llm-evals`, `fine-tuning`) + motivation; default `rag-engineer` |
| **Return visit** | If `GET /me/forges` has items → **Continue** / **View all** (`/forges`) / **New forge** (+ optional Forge again); if zero artifacts but `GET /me/profile` has diagnosis → Welcome back (**Forge again** / **New from scratch**); if diagnosis on ready gate → **Forge again from last diagnosis** (hydrate → `/onboarding/edit` or forge from profile). Zero artifacts + no diagnosis → GoalPicker only |
| **Route** | `/` · `data-screen="goal-picker"` or `landing-recovery` |

---

### 1b. Forges list (`/forges`) — CAR-29 / CAR-31

Catalog of historical forge artifacts. Primary job: **scan & open**. Visible: **Open** (freeze-before-promote) + **Rename**. Quiet overflow (**⋯**): copy **share**, copy **resume**, **Revoke share**. Untitled default titles (`Roadmap · {goal}` / `Roadmap`) display as `goal_id` (or `Roadmap`) so goal is not duplicated in meta. Optional **Forge again from last diagnosis** when profile has diagnosis.

| | |
|---|---|
| **Route** | `/forges` · `data-screen="forges-list"` |
| **API** | `GET /me/forges` · `PATCH /me/forges/{public_id}` (title) · `POST …/share/revoke` |

### 1c. Share / resume deep-links — CAR-27/29

| Link | App route | API (Labs same-origin) | Behavior |
|------|-----------|------------------------|----------|
| Share | `/share/[token]` · `data-screen="share-readonly"` | `GET /public/share/{token}` | Read-only roadmap from artifact snapshot; **does not** adopt owner `user_id` |
| Resume | `/resume/[token]` · `data-screen="resume-consume"` | `POST /public/resume/{token}` | Consumes token; if local Bearer has forges **and** `external_id` ≠ resume owner → **conflict chooser** (keep local / switch) before `adoptSession`; else adopt → open roadmap; second use fails |

Copied links use **app** paths (`/share/…`, `/resume/…`), not `/public/…`.

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
| **Soft gate (CAR-15)** | When diagnosis `soft_gated` → **Lean roadmap** warning banner above the lists (`data-testid="soft-gate-warning"`). Copy from API `soft_gate_warning`. Does **not** block confirm/forge |
| **Why** | The confirmation screen was a dead-end — no feedback, no agency |
| **Route** | `/onboarding/edit` · `data-testid="editable-diagnosis"` |
| **Shipped** | HAC-53 — view/edit modes per item; strengths/gaps editable; priorities reorderable · CAR-15 soft-gate banner |
| **On confirm** | `POST /diagnosis/confirm` persists the profile → `POST /forge/runs` → SSE. Soft-gate prune applied on BE forge input when below bar |

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
| **Soft gate (CAR-15)** | At forge entry, if session diagnosis is `soft_gated` → same lean warning (`data-testid="soft-gate-warning-forge"`). Stream UX unchanged |
| **Route** | `/roadmap/forge` · `data-screen="forge-stream"` (app: `/forge`) |

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
| **Route** | `/roadmap/forge/complete` · `data-screen="forge-reveal"` (app: `/forge/complete`) |
| **CAR-27** | After reveal, show **resume link copy once** (single-use ~7d) beside roadmap CTA |
| **CAR-29** | Optional **email store** (`PATCH /me/email`) — no send; for future CAR-28 delivery |

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
- **References** section (real links when they come from web search) — opens `/reference?node=&item=` inside Career Forge; mark as studied remains a separate act
- **Study progress** bar (`x/y` completed) when there are items; copy makes clear this does not replace AI validation
- **Chapter tutor** (`open-tutor-drawer`) — optional technical Q&A; no inline mentor chat in the drawer
- CTA **Mock interview — validate mastery** (real proof of learning)

---

### 6b. Reference viewer (`/reference`) — CAR-85

**User job:** Study one Node Reference without losing the Roadmap context.

| | |
|---|---|
| **Address** | `node` + Reference `item`; never a raw `url` query |
| **Chrome** | Node title, this Reference's `done` control, sibling References, CTA back to the Node drawer |
| **Preview** | Best-effort sandboxed iframe; persistent **Open on source site** escape hatch in a new tab |
| **Invalid** | Missing/unknown Node or item returns to `/roadmap`; no empty viewer |
| **Out** | `/learn`, tutor/mentor links, Live Forge sources, persisted “opened” event |

Opening a Reference never marks it done. The viewer uses the existing checklist command.

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
| Forge recovery (landing / forges / share / resume / email / re-forge) | ⬜ Not in prototype — **code + this doc win** (CAR-27/29 / ADR-003) |
| Soft gate lean warning (CAR-15) | ⬜ Not in prototype — **code + this doc win** (banner on edit + forge entry) |

Implementation target: this doc + [SCREEN-INTENT.md](./SCREEN-INTENT.md).

---

*Last updated: 2026-08-03 — CAR-15 ui-product-sync: soft-gate warning on diagnosis edit + forge entry*
