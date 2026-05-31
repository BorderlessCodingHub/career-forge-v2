# Product Vision — Career Forge

> North star for UI and demo narrative. Authority: [PRODUCT-SOURCE-OF-TRUTH](./PRODUCT-SOURCE-OF-TRUTH.md) · [CHECKPOINT](../docs/CHECKPOINT.md)

---

## One sentence

**Career Forge** continuously models the professional growth of someone becoming a developer — diagnosis, a living roadmap, mastery validation, and evidence for mentors.

---

## Positioning

| They | We |
|------|-----|
| roadmap.sh — one generic path for everyone | A roadmap **personalized** by goal and starting point |
| Manual checklist / "mark as done" | **Mastery before progression** — AI interview before advancing |
| Generic AI tutor in the corner | AI as the **operating system** of the journey |
| No evidence for the mentor | **Learning evidence** — scores, gaps, structured recommendations |

Official sub-theme: **Learn with practical validation** (Alpha School: demonstrated mastery > content consumed).

---

## Five pillars (demo must show)

### 1. Career Forge — identity engine

The user declares **who they want to be** and **why** (motivation). The goal feeds diagnosis, forge, and prioritization — it is not a decorative dropdown.

- MVP: one active roadmap (Backend Developer)
- Other roadmaps: "Coming soon" in the UI

### 2. Skill graph — adaptive brain

A personalized dependency graph with states and mastery % — a living roadmap, not a static checklist.

- Base catalog: `data/roadmap.json` (topics + prerequisites + rubric)
- Dynamic state: status per node + accumulated evidence
- **Steady state UI:** vertical roadmap.sh-style layout (spine + categories + left/right nodes)
- Status: `bloqueado | recomendado | em_estudo | validar | aprovado | revisar`

### 3. Live Roadmap Forge — wow #1

After the **editable** diagnosis, the user clicks **"Generate roadmap"** and **watches** the AI forge the roadmap:

- Live timeline — numbered steps 1, 2, 3, 4… (reasoning, artifacts, decisions)
- **No graph visible during the stream** — full focus on the AI's thinking
- Animation reveal — items fly into the vertical layout
- Roadmap ready + next mission

Expected reaction: *"I'm watching the AI think and build MY roadmap."*

Technical spec: [stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md) · Flow: [UX-FLOW.md](./UX-FLOW.md)

### 4. Mastery validation — wow #2

**Validate with AI** button — short interview, score 0–100, actionable feedback.

- Does not approve vague answers
- Generates `mentor_summary` for Borderless
- Reaction: *"It won't let me pretend I learned."*

### 5. Borderless mentor value

Ambassadors judge internal usefulness. The product must show:

- Where the learner got stuck (gaps from validation)
- Objective evidence (not self-reporting)
- Recommended next step (P1: contextual mentor; P1: simple report)

Line for judges: *"Reduces the mentor's manual work — gaps and evidence already structured."*

---

## Adaptive loop (P0 narrative)

```
Goal → Diagnosis → Forge → Graph → Validate → Graph reacts → (contextual mentor)
```

Mandatory demo scene: a **bad** validation on REST → HTTP rises in priority → mission updated.

---

## Out of scope (hackathon)

Do not build UI for these in MVP (see [CHECKPOINT](../docs/CHECKPOINT.md)):

- Multiple complete roadmaps
- Enterprise auth / classes
- Gamification (badges, ranking, streaks)
- GitHub integration
- Mock interview loop (P1 stretch)
- CV from evidence (P2)

---

## Success metrics (qualitative, demo)

| Moment | Pass |
|--------|------|
| Editable diagnosis | User adjusts item, clicks "Generate roadmap" |
| Forge | Timeline-only stream with numbered steps < 60s in demo |
| Reveal | Items animate into vertical roadmap layout |
| Validation | Score + gaps + next step in one screen |
| Adaptive | Roadmap visibly changes after failed validation |
| Mentor (P1) | Answer references last validation, not generic tips |

---

## References

- [UX-FLOW.md](./UX-FLOW.md) — canonical flow (HAC-21)
- [handoff_chat_gpt.txt](../docs/handoff_chat_gpt.txt) — team debate + judge reframing
- [prototype/](./prototype/) — tokens/components (flow may lag docs)
- [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png) — steady-state layout
