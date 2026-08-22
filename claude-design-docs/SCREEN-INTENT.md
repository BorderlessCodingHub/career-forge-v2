# Screen Intent — Career Forge

> **Per-screen must-match for agents.** Non-negotiable UX constraints.  
> Flow narrative: [UX-FLOW.md](./UX-FLOW.md) · Route table: [SCREEN-INTENT-MAP.md](./SCREEN-INTENT-MAP.md)

---

## Global rules

- Product UI copy: **English** (CAR-16). Marketing `/welcome` ships EN (CAR-56 Premium B); **pt-BR marketing + chrome** = CAR-37
- Status enum: `bloqueado | recomendado | em_estudo | validar | aprovado | revisar` — never rename without CHECKPOINT + API
- No gamification (confetti, XP, streaks) on **product** UI. Welcome ApplicationModal may use confetti (Welcome-scoped only). Premium A HTML preview remains theater.
- P0 wow moments must survive: **Forge stream**, **Animation reveal**, **Validation**, **Adaptive roadmap**

---

## 0. Marketing welcome (`/welcome`) — MUST match (CAR-56 · Premium B)

Supersedes CAR-35 screen-intent for this route. Spec lock: CAR-54.

| Constraint | Detail |
|------------|--------|
| Route | `/welcome` under `basePath=/career-forge` — **not** a thin layer replacing `/` |
| Look | Commercial Premium B (slate/orange Vite chrome) via `components/marketing/welcome/` — **not** CAR-34 product tokens / BrandMark on first cutover |
| Language | EN; pt-BR → CAR-37 |
| Conversion | Nav / hero / final primary → Next `Link` `/` · **Start diagnosis** · `data-testid="welcome-cta-start"` (desktop + mobile nav variants). Local B-styled links — do **not** reuse `StartDiagnosisCta` |
| Scenery | Claim Scholarship, Syllabus, Strategy, other Apply → modals (Apply + Strategy + Syllabus). Pricing/apply theater is scenery |
| Proof | Fake social proof / testimonials allowed until CAR-53 honesty pass |
| Font | `Plus_Jakarta_Sans` via `next/font` on Welcome shell only. Product stays Inter |
| CSS | `welcome/welcome.css` imported only from Welcome shell. Welcome-scoped confetti OK in ApplicationModal only |
| Out | Real Stripe / waitlist / email · Google Fonts `<link>` · restyling to BrandMark on cutover |
| Product `/` | Unchanged — `LandingRecoveryGate` / GoalPicker |
| Hook | `data-screen="marketing-welcome"` · `data-testid="welcome-cta-start"` |
| Redirect | `/welcome/premium-b` → `/welcome` (permanent) |

**Can evolve:** pt-BR (CAR-37); CAR-53 honesty pass; BrandMark polish

---

## 0b. Marketing welcome PLG (`/welcome/plg`) — MUST match (exploration)

Direct URL only. **Do not** replace `/welcome` or add a chooser there.

| Constraint | Detail |
|------------|--------|
| Route | `/welcome/plg` · `data-screen="marketing-welcome-plg"` |
| Genre | Product-led (Granola rhythm) |
| Must | Split hero + HTML/CSS forge mock **stays on the first fold**; trail / phases / features slide into the remaining viewport; split-flap plaque (audience → phases → features); before/during/after; dark tokens; EN; Start diagnosis → `/` |
| Out | Pricing · email · checkout · fake testimonials · fake logo wall · editorial/offer variants |

---

## 0c. Premium landing preview A (`/welcome/premium-a`) — bake-off only (CAR-41)

Direct URL only. **Do not** link from `/welcome` / `/welcome/plg`. Premium B preview URL redirects to `/welcome` (CAR-56).

| Constraint | Detail |
|------------|--------|
| Route | `/welcome/premium-a` under `basePath=/career-forge` |
| Serve | Next rewrite → committed Vite single-file HTML (`public/premium-landings/a.html`) |
| Fidelity | Pixel clone of `claude-design-docs/premium-landings/a/` including pricing and fake apply/strategy UI |
| Out of funnel | CTAs do **not** go to `/`; Apply/Strategy stay client-only theater; `noindex,nofollow`; title `· preview` |
| Source | [premium-landings/README.md](./premium-landings/README.md) · regenerate A with `make premium-landings` |
| B Vite folder | Frozen history at `claude-design-docs/premium-landings/b/` — not built; living SoT is Next `marketing/welcome/` |

**Can evolve:** keep or retire Premium A later; do not resurrect `b.html`

---

## 1. Goal Picker — MUST match

| Constraint | Detail |
|------------|--------|
| Headline | *"Where do you want to go?"* |
| Subhead | Optional — keep minimal; no long explanatory paragraph required |
| Cards | **Four** v2 LLM tracks (all active): `rag-engineer`, `agent-engineer`, `llm-evals`, `fine-tuning` — labels from `CAREER_GOALS` in `onboarding-data.ts` |
| Default | `rag-engineer` pre-selected |
| Layout | **Minimal** — compact row cards, no heavy chrome (icons, meta badges, footer notes) |
| Motivation | Required in happy path — feeds downstream AI |
| CTA | Single primary action to onboarding |
| Recovery (CAR-27/29) | If ≥1 forge artifact → **Continue** / **View all** / **New forge**; if saved diagnosis (even with zero artifacts) → **Forge again from last diagnosis** (`landing-reforge-profile`); empty + no diagnosis → GoalPicker (`data-screen="landing-recovery"`) |

**Can evolve:** hover states, validation toast, animation library

---

## 1b. Forge recovery surfaces (CAR-27/29) — MUST match

| Constraint | Detail |
|------------|--------|
| `/forges` | Scan & open: primary **Open** + **Rename**; Copy share / Copy resume / Revoke share in page-local **⋯** overflow; untitled default title shows `goal_id` (not `Roadmap · {goal}`); active badge; optional re-forge from profile when diagnosis exists |
| Share | App route `/share/[token]` (read-only); API `GET /public/share/{token}` — **never** adopts owner session |
| Resume | App route `/resume/[token]`; API `POST /public/resume/{token}` — if local forges exist for a **different** `external_id` → chooser (**Keep local** / **Switch to resume**) before `adoptSession`; else auto-adopt → roadmap; second use / expiry must fail clearly |
| Forge complete | Resume link **copy once** after reveal (`forge-resume-copy`); optional email store (`forge-email-store`) — **no SMTP** |
| Landing / forges | When `GET /me/profile` has diagnosis → **Forge again from last diagnosis** (`landing-reforge-profile` / `forges-reforge-profile`) — hydrate session → `/onboarding/edit` or forge from profile; **New from scratch** still → GoalPicker + interview |
| Copy | Recovery surfaces are English (CAR-16) |
| Forbidden | Silent overwrite of conflicting local sessions; email **send** (CAR-28); mid-flight interview resume |

---

## 2. Onboarding diagnostic — MUST match

| Constraint | Detail |
|------------|--------|
| Feel | Focused diagnostic — **not** open-ended ChatGPT |
| Layout | **Pill/balloon rounds** — multiple questions shown together per round |
| Rounds | 3 batches: seniority/context → stack/domain → gaps (Git, HTTP, APIs, DB) |
| Input | Each pill has its own textarea — **not** one-at-a-time chat bubbles; explicit short negative answers like "Nothing." are valid signal |
| Progress | Step indicator + round counter (e.g. Round 2/3) |
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
| Add | User can add items to strengths / gaps / recommendation |
| Remove | User can remove items |
| Profile badge | e.g. "Beginner with a JavaScript foundation" |
| Evidence callout | Evidence-based assessment — no fake "done" |
| Soft gate (CAR-15) | When `soft_gated` → **Lean roadmap** status banner (`soft-gate-warning`) with API copy; **does not** replace CTA or block forge |
| CTA | **"Generate roadmap"** — explicit forge trigger |
| Forbidden | Read-only confirmation with passive "View my roadmap" dead-end; hard-blocking soft gate on this screen |

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
| Header | "Forging your personalized roadmap" + elapsed / steps |
| Soft gate (CAR-15) | Optional lean warning at entry (`soft-gate-warning-forge`) when below bar — status only; timeline stream unchanged |
| Exit | On `graph_ready` → show manual **"View roadmap"** CTA → animation reveal |

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
| Post-reveal (CAR-27/29) | Resume link **copy once** (`forge-resume-copy`); optional email store (`forge-email-store`) — store only, no send |

**Can evolve:** Framer Motion vs CSS, duration, stagger timing

---

## 6. Vertical roadmap (steady state) — MUST match ⭐ ARTIFACT MODE (HAC-25)

| Constraint | Detail |
|------------|--------|
| App mode | **`artifact`** — finished personalized roadmap.sh page; distinct from **`setup`** (onboarding + forge) |
| Layout | Full-width vertical spine; nodes alternating left/right with **solid horizontal connectors** to spine dot (`roadmap-connector-{id}`); category headers |
| Reference | [roadmap-sh-reference-full.png](./references/roadmap-sh-reference-full.png) · [roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) |
| Chrome | **No** onboarding stepper (01 Goal … 07 Adaptation); **no** fixed progress/evidence/mentor sidebar |
| Top bar | Career Forge logo + **Your roadmap** track name; right cluster **`items-end`** — **`mentor-report-link`** action bottom-aligned with track title line; same `topbarActionClass` (`h-9`); report = `h-7` icon slot + `FileText` + label; **no** progress ring in topbar; mentor via node drawer only |
| Page intro | Subtitle/hint + optional centered **`trail-progress-ring`** below subtitle (`getTrailChecklistProgressPct` — item-pooled checklist %, not mastery %, not topic-average) + **Study progress** label — **no** duplicate track `<h1>` on canvas |
| Canvas nodes | **Uniform** Borderless purple cards — compact **study** progress (`x/y` + mint bar) when checklist items exist; **mastery %** and status detail stay in **node drawer** only |
| Interaction | **Click node** → right drawer: title, red **✕** dismiss, Escape to close, status/mastery, study progress, description callout when no gaps, collapsible outcomes/refs/tasks (default expanded), optional tutor row, sticky CTA **Mock interview — validate mastery** |
| Personalization | Graph state still adaptive (backend recalibrates) — visible in drawer, not canvas pollution |
| Forbidden | Forge streaming as steady state; MissionBanner hero on artifact canvas; status-colored node grid |

**Can evolve:** drawer width, reference API, full AI tutor panel vs mini chat

---

## 7. Mastery validation — MUST match

| Constraint | Detail |
|------------|--------|
| Headline | *"Ready to validate your learning?"* |
| Subhead | Interview before unlocking the next topic |
| Flow | Question card + textarea + submit |
| Result | ScoreRing, status pill, got right / improve / next step |
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

## 9. Mentor evidence report (`/report`) — MUST match

| Constraint | Detail |
|------------|--------|
| Entry | Topbar **`mentor-report-link`** on artifact routes → `/report` |
| Goal | Human career goal label from `CAREER_GOALS` map (`formatGoalForDisplay`) — **never** raw slug (`rag-engineer`) |
| Topic headline | Human-readable title — **never** raw slug (`node-1-…`) as primary label; `formatNodeTitleForDisplay` fallback humanizes hyphens |
| Validation card | Score + status pill; **`mentor-report-entry-{node_id}`** |
| Mentor summary | Structured sections — **Main gaps** (bullets), **Positive evidence** (bullets when present), **Next step** (intervention callout) — not a single dense paragraph |
| Legacy rows | When structured fields empty, split cleaned `mentor_summary` into short lines (strip `(node-id)` parenthetical) |
| Forbidden | Showing internal `node_id` as the topic title; wall-of-text mentor resume |

**Can evolve:** export PDF, filtering by validation date

---

## Verification hooks (Playwright Gate B)

| Screen | `data-testid` |
|--------|---------------|
| Goal picker | `goal-picker` |
| Landing recovery | `landing-continue` · `landing-view-all` · `landing-new-forge` · `landing-reforge-profile` · `landing-recovery-fallback` |
| Forges list | `forge-row-{public_id}` · `forge-open-{id}` · `forge-rename-{id}` · `forge-overflow-{id}` · `forge-title-input-{id}` · `forge-title-save-{id}` · `forge-share-{id}` · `forge-revoke-{id}` · `forge-resume-{id}` · `forges-reforge-profile` |
| Share read-only | `share-node-list` · `share-error` |
| Resume consume | `resume-working` · `resume-conflict` · `resume-keep-local` · `resume-switch` · `resume-error` · `resume-home` |
| Forge complete resume | `forge-resume-copy` · `forge-resume-copy-btn` |
| Forge complete email | `forge-email-store` · `forge-email-input` · `forge-email-save` · `forge-email-error` |
| Editable diagnosis | `diagnosis-editable` |
| Forge timeline | `forge-timeline` |
| Vertical roadmap | `vertical-roadmap` |
| Trail progress ring | `trail-progress-ring` (page intro, not topbar) |
| Spine canvas | `vertical-spine` · `roadmap-connector-{id}` |
| Mentor report | `mentor-report` · `mentor-report-entry-{node_id}` |
| Validation score | `validation-score` |

---

*Last updated: 2026-08-03 — CAR-15 ui-product-sync: soft-gate lean warning on edit + forge*
