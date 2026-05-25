# CHECKPOINT — Career Forge product

> **Navigation:** [ROADMAP](./ROADMAP.md) · [STATUS](./STATUS.md) · [claude-design-docs](../claude-design-docs/)

Authoritative product + architecture reference for agents.

---

## One-liner

**Career Forge** — skill graph adaptativo que diagnostica, forja trilha ao vivo, valida mastery e gera evidências para mentores.

Sub-eixo: **Aprender com validação prática** (Alpha School: mastery before progression).

**Audience:** career transition to tech (often zero or early study) — not senior hiring.

**AI-first rule:** remove AI → app stops. Identity/diagnosis **must** be LLM-driven ([ADR-001](./decisions/ADR-001-adaptive-diagnosis-ctrr.md)).

---

## Wow features (priority)

| P | Feature | User reaction |
|---|---------|---------------|
| P0 | **Live Roadmap Forge** | "Tô vendo a IA pensar e montar MINHA trilha" |
| P0 | **Mastery Validation** | "Não deixa eu mentir que aprendi" |
| P0 | **Adaptive graph** | "A trilha mudou porque eu errei" |
| P1 | Contextual Mentor | "Sabe onde eu travei" |
| P1 | Mock → recalibra | "Entrevista muda o plano" |

---

## Stack (closed)

```
apps/frontend/     Next.js + TS + Tailwind
apps/backend/     FastAPI + Pydantic + SQLAlchemy
PostgreSQL    skill graph state, validations, profiles, graph_runs
LangGraph     diagnosis_graph, roadmap_forge_graph, validation_graph
LangChain     astream_events v2 via GraphExecutor (HAC-32)
LangSmith     traces per GraphRun
```

## AI execution layer (HAC-32)

Unified under `career_forge/ai/`:

- **GraphRun** — one execution record (id, graph_name, user_id, status, I/O, events)
- **AgentFactory** — `factory.get("roadmap_forge")` → configured runnable
- **GraphExecutor** — always `astream_events` v2; `stream=False` collects, `stream=True` → SSE

Canonical doc: [engineering/EXECUTION-FLOW.md](./engineering/EXECUTION-FLOW.md) · [engineering/AI-EXECUTION.md](./engineering/AI-EXECUTION.md)

---

## Live Roadmap Forge (HAC-18)

Post-onboarding LangGraph loop:

1. `load_topics` — roadmap.json catalog
2. `analyze_gaps` — LLM streams reasoning
3. `research_enrich` — history + feedback
4. `accumulate_graph` — **Python merge** into SkillGraphState (LLM proposes, code disposes)
5. `should_continue` — max 3 iterations
6. `emit_final` — SSE `graph_ready`

SSE events: `reasoning_delta`, `artifact_found`, `node_updated`, `step_complete`, `graph_ready`

Full spec: [stack-and-roadmap-forge.md](./stack-and-roadmap-forge.md)

---

## Skill graph model

**Static catalog:** `data/roadmap.json` — nodes, prerequisites, outcomes, rubric

**Dynamic state:** `user_skill_nodes` — status, mastery_score, evidence[]

Statuses: `bloqueado | recomendado | em_estudo | validar | aprovado | revisar`

---

## UI reference

Canonical UX (HAC-21): [claude-design-docs/UX-FLOW.md](../claude-design-docs/UX-FLOW.md) · [SCREEN-INTENT.md](../claude-design-docs/SCREEN-INTENT.md)

Claude Design prototype: [claude-design-docs/prototype/](../claude-design-docs/prototype/) — tokens/components only; flow may lag docs.

**Visual identity (HAC-23):** Borderless Community theming — deep purple-black, purple roadmap nodes, cyan progress, sidebar + canvas shell. Canonical: [BORDERLESS-THEMING.md](../claude-design-docs/BORDERLESS-THEMING.md). Primary reference: [borderless-code-breakers-dashboard.png](../claude-design-docs/references/borderless-code-breakers-dashboard.png). Steady state: canvas roadmap + optional AI sidebar (roadmap.sh layout secondary).

---

## Adaptive diagnosis (ADR-001 — in progress HAC-42–46)

Screen 2: **CTRR** rubric + Interviewer/Judge loop — max 2 questions/turn, optional PDF CV, accumulative transcript → `DiagnosisResponse`.

Spec: [product/DIAGNOSIS-INTERVIEW.md](./product/DIAGNOSIS-INTERVIEW.md)

---

## Demo script (5 min)

1. Goal + motivation (+ optional CV)
2. AI diagnosis interview → diagnóstico editável
3. **Editable diagnosis** — ajustar lacuna, clicar **"Gerar roadmap"**
4. **Forge stream** (timeline passos 1–N, sem grafo) → **animation reveal** → vertical roadmap
5. Validar REST → resposta ruim → score
6. Roadmap reage + sugestão mentor / AI sidebar

---

## Out of scope (hackathon)

- Multiple full tracks
- Enterprise auth
- Gamification
- GitHub integration
- Web scraping for research (MVP: LLM-labeled research steps)

---

*HB01-2026 · Programadores Sem Pátria*
