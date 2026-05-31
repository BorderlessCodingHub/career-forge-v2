# Claude Design — Career Forge

UI documentation generated in Claude Design, per-screen product intent, and the **source of truth** for agents implementing the front-end.

---

## Start here (agents)

| Doc | Purpose |
|-----|---------|
| **[PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md)** | **Canonical** — hierarchy, flow summary, implementation notes |
| **[BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md)** | **Canonical theming** — Borderless palette, shell, canvas, nodes (HAC-23) |
| **[UX-FLOW.md](./UX-FLOW.md)** | Screen-by-screen flow + old vs new paradigm (HAC-21) |
| **[SCREEN-INTENT.md](./SCREEN-INTENT.md)** | Per-screen must-match constraints |
| [PRODUCT-VISION.md](./PRODUCT-VISION.md) | North star, pillars, demo narrative |
| [UI-PRINCIPLES.md](./UI-PRINCIPLES.md) | Visual DNA, tokens, component patterns |
| [design-tokens.md](./design-tokens.md) | Borderless color/type tokens |
| [MOCK-PROTOTYPE-PLAN.md](./MOCK-PROTOTYPE-PLAN.md) | HTML prototype evolution (Phase 1–4) |
| [UI-SUGGESTIONS-BACKLOG.md](./UI-SUGGESTIONS-BACKLOG.md) | User UI feedback backlog |
| [SCREEN-INTENT-MAP.md](./SCREEN-INTENT-MAP.md) | Route table + quick reference |

**Before UI work:** read PRODUCT-SOURCE-OF-TRUTH → UX-FLOW → SCREEN-INTENT → [BORDERLESS-THEMING](./BORDERLESS-THEMING.md) → open [Code Breakers reference](./references/borderless-code-breakers-dashboard.png) → read [docs/CHECKPOINT.md](../docs/CHECKPOINT.md).

**After UI paradigm change:** update PRODUCT-SOURCE-OF-TRUTH (rule: [.cursor/rules/ui-product-sync.mdc](../.cursor/rules/ui-product-sync.mdc), skill: [.cursor/skills/ui-product-sync/SKILL.md](../.cursor/skills/ui-product-sync/SKILL.md)).

---

## Canonical flow (HAC-21)

```
Goal → Onboarding chat → Editable diagnosis → [Generate roadmap] → Forge stream (steps only) → Animation reveal → Vertical roadmap + optional AI sidebar
```

Details: [UX-FLOW.md](./UX-FLOW.md)

---

## Prototype

Files exported from Claude Design (standalone React via Babel):

| File | Contents |
|---------|----------|
| [prototype/index.html](./prototype/index.html) | Redirect entry — use with local server |
| [prototype/README.md](./prototype/README.md) | **How to run** — `python3 -m http.server 8765` |
| [prototype/Career Forge.html](./prototype/Career%20Forge.html) | Main app entry |
| [prototype/app.jsx](./prototype/app.jsx) | Router / shell |
| [prototype/screens-flow.jsx](./prototype/screens-flow.jsx) | Onboarding + goal picker + diagnosis result (legacy) |
| [prototype/screens-forge.jsx](./prototype/screens-forge.jsx) | Live Roadmap Forge + reveal (legacy split layout) |
| [prototype/screens-dashboard.jsx](./prototype/screens-dashboard.jsx) | Skill graph steady state (legacy) |
| [prototype/skill-graph.jsx](./prototype/skill-graph.jsx) | Graph + nodes |
| [prototype/components.jsx](./prototype/components.jsx) | Design system components |
| [prototype/styles.css](./prototype/styles.css) | Tokens + layout |

```bash
cd claude-design-docs/prototype
python3 -m http.server 8765
open http://localhost:8765/
```

Legacy URL `Career OS.html` redirects automatically.

### Prototype drift

> **HAC-21:** The HTML prototype reflects the **old** paradigm (read-only confirmation, split forge with graph, skill-graph dashboard). Use it for **tokens and components**, not for flow or steady-state layout.

| Aspect | Prototype (legacy) | Docs (HAC-21 truth) |
|---------|-------------------|---------------------|
| Post-diagnosis | Read-only result | Editable diagnosis + "Generate roadmap" |
| Forge | Timeline + graph skeleton | Timeline only |
| Steady state | Skill graph dashboard | Vertical roadmap + optional AI sidebar |

Update the prototype: future issue (HAC-9 / HAC-18 UI).

---

## Visual positioning (Borderless — HAC-23)

- **Identity:** Borderless Community — deep purple + mint/cyan, sidebar shell + canvas (Code Breakers)
- **Inspired by** [roadmap.sh](https://roadmap.sh) — optional AI tutor sidebar (secondary layout)
- **Evolved into** an adaptive skill graph on canvas — purple nodes, mint progress, dashed dependencies
- **Not** a generic LMS, gamification, or legacy indigo navy

References: [borderless-code-breakers-dashboard.png](./references/borderless-code-breakers-dashboard.png) · [borderless-logo-brand.png](./references/borderless-logo-brand.png)

Details: [BORDERLESS-THEMING.md](./BORDERLESS-THEMING.md) · [UI-PRINCIPLES.md](./UI-PRINCIPLES.md)

---

## Screens (demo flow — HAC-21)

| # | Route | Name | Wow |
|---|------|------|-----|
| 1 | `/` | Goal Picker | Goal + motivation |
| 2 | `/onboarding` | AI Diagnosis | Pill rounds — 2 questions/round, 3 rounds |
| 3 | `/onboarding/edit` | **Editable diagnosis** | User corrects strengths/gaps |
| 4 | `/roadmap/forge` | **Live Roadmap Forge** | Streaming timeline (steps 1–N) — no graph |
| 4b | `/roadmap/forge/complete` | **Animation reveal** | Items fly into the vertical layout |
| 5 | `/roadmap` | **Vertical roadmap** | Steady roadmap + optional AI sidebar |
| 6 | `/validate/:topic` | Mastery Validation | Interview + score |
| 7 | `/roadmap` (updated) | Adaptive + Mentor | Roadmap reacted after validation |

Full intent: [SCREEN-INTENT.md](./SCREEN-INTENT.md) · [UX-FLOW.md](./UX-FLOW.md)

---

## Live Roadmap Forge (hero UX — HAC-21)

After the editable diagnosis, the user clicks **"Generate roadmap"** and **watches the AI think**:

**During generation — timeline only:**
- Numbered steps 1, 2, 3, 4…
- Reasoning (`reasoning_delta`)
- Artifacts (`artifact_found`)
- Decisions (`decision`)
- **No skill graph visible**

**On completion:**
- Animation — each stream item flies into the vertical layout
- Transition to steady state at `/roadmap`

Mocked script in `screens-forge.jsx` (`FORGE_SCRIPT`) — the real implementation uses SSE from FastAPI + LangGraph. The UI consumes timeline only; `node_updated` feeds backend state, not a visual preview during the stream.

Spec: [docs/stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md)

---

## Design tokens

See [design-tokens.md](./design-tokens.md) and `prototype/styles.css`.

---

## Handoff → Next.js

When implementing:

1. Extract tokens → `tailwind.config.ts`
2. Map components → `apps/frontend/components/`
3. Follow the routes in [UX-FLOW.md](./UX-FLOW.md) — not the prototype's legacy hash routes
4. Forge timeline → consumes `EventSource` SSE (timeline only)
5. Reveal → Framer Motion (items → vertical roadmap positions)
6. Steady state → vertical roadmap layout + collapsible AI sidebar

Record divergences in [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md) → Implementation notes.

---

## Implementation stack

The front-end consumes the FastAPI API. See [docs/stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md) · Product: [docs/CHECKPOINT.md](../docs/CHECKPOINT.md)
