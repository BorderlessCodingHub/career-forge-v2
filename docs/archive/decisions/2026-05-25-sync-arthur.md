# Sync Arthur — Career Forge scope & sprint decisions

**Date:** 2026-05-25  
**Meeting:** sync (Granola id `c0d6bcc2-4e2e-48b8-b0ad-fd006ba106e7`)  
**Participants:** Matheus Oliveira Silva, Arthur (sync call)

> Source: Granola meeting summary — [sync, 25 May 2026](granola://meeting/c0d6bcc2-4e2e-48b8-b0ad-fd006ba106e7)

---

## Context

Alignment on scope, stack, team split, and MVP goal before hackathon week. Demonstration of the Career Forge concept to Arthur.

---

## Decisions — FIT (in scope)

| Decision | Detail | Linear mapping |
|----------|--------|----------------|
| **Specialized backend focus** | Roadmap for backend devs with a specific goal (e.g., APIs for space tech) | HAC-8, HAC-6 |
| **Contextual diagnosis** | AI asks questions based on the goal; generates strengths, gaps, recommendations | HAC-8 |
| **Live Roadmap Forge** | Roadmap generated in real time with AI streaming (+ enriched web search) | HAC-18 |
| **Validation via mock interview** | After each topic, the AI interviews before unlocking progress | HAC-10, HAC-14 |
| **Adaptive roadmap** | Assessment failure → new branch / reprioritization | HAC-11 |
| **Integrated contextual chat** | Ask for references or clarify questions with memory of progress | HAC-13 |
| **Differentiator vs generic roadmap** | Personalization by goal + résumé; proprietary AI knows individual progress | HAC-8, HAC-18, CHECKPOINT |
| **Locked stack** | Frontend TypeScript (Arthur) · Backend Python FastAPI + LangChain | HAC-5 |
| **Shared OpenAI token** | $10 dev credit shared across the team | HAC-5 (env setup) |
| **Parallel development** | Linear issues per feature; P batches when possible | SPRINT-BOARD Sprint 1, 5 |
| **MVP by Thursday** | Functional target ~2026-05-29 (not Sunday) — margin for polish | Milestones Sprint 1–4 |
| **Deploy** | Vercel (web) + VPS/Railway (api) after local dev | HAC-5 |
| **7-min pitch** | Live demo of the full flow; focus on mock interview validation | HAC-12 (demo mode) |

---

## Decisions — NO FIT / deferred (won't do this week)

| Item | Reason | Linear |
|------|--------|--------|
| Daily tracking, GitHub-contributions style | Gamification — not the product engine | HAC-28 (Cancelled) |
| Levels/titles system (apprentice → global) | Gamification — post-MVP polish | HAC-28 |
| Automatic progress posts on the platform | Social/feed — outside the core demo | HAC-29 (Cancelled) |
| Onboarding with hours/day to break down the roadmap | Nice-to-have pacing — defer post-Thursday | HAC-30 (Cancelled) |
| Multiple complete roadmaps (fullstack, data, frontend) | Scope — one well-built backend roadmap | CHECKPOINT out-of-scope |
| Auth enterprise / multi-tenant | Demo with a fake user or simple login | CHECKPOINT |
| Aggressive content web scraping | Technical risk; MVP uses LLM + JSON catalog | HAC-18 (research_enrich simplified) |
| CV from evidence (P2) | Stretch — only if P0 is flawless | HAC-16 (Backlog P2) |

---

## Team split

| Person | Ownership |
|--------|-----------|
| **Arthur** | Frontend TypeScript / Next.js |
| **Matheus** | Harness, backend bootstrap, agent coordination, mock of the 2 main screens (by the night of 25/05) |
| **Backend Python** | FastAPI + LangGraph (shared) |

> Arthur's participation pending formal confirmation (call note).

---

## Action items → Linear

| Action | Owner | Issue |
|--------|-------|-------|
| Bootstrap frontend + mock 2 main screens | Matheus | HAC-5 (partial), HAC-8 |
| Set up Cursor for accelerated dev | Matheus | HAC-19 ✅ |
| Sprint roadmap + agent lifecycle docs | Matheus | HAC-30 |
| Confirm Arthur's participation | Matheus → Arthur | — |
| Functional MVP by Thursday | Team | Milestones Sprint 1–4 |
| 7-min pitch rehearsed | Team | HAC-12 |

---

## Technical direction (confirmed)

```
Onboarding diagnosis → Live Forge (SSE) → Vertical roadmap artifact
  → Validate with AI (mock interview) → Roadmap reacts → Contextual mentor (P1)
```

Pitch narrative: *"A roadmap that doesn't accept manual check-offs — the AI diagnoses, forges live, interviews, and adapts."*

---

*Next review: after Sprint 1 Foundation merge (HAC-5/6/7)*

---

## Historical note (post-MVP evolution)

The deploy decision above reflects the 2026-05-25 meeting context. Current production baseline evolved to GHCR + VPS (host nginx + `docker-compose.prod.yml`) documented in [docs/engineering/DEPLOY-VPS.md](../engineering/DEPLOY-VPS.md).
