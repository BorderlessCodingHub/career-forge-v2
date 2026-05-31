# Closed stack + Live Roadmap Forge

## Official stack

| Layer | Technology |
|--------|------------|
| Frontend | Next.js + TypeScript + Tailwind |
| Backend | FastAPI + Pydantic + SQLAlchemy/Alembic |
| Database | PostgreSQL |
| AI orchestration | LangGraph + LangChain |
| Observability | LangSmith |
| Deploy | GHCR + VPS (host nginx + `docker-compose.prod.yml`) + Postgres |
| Local dev | docker-compose (web + api + postgres) |

Monorepo:
```
apps/frontend/          # Next.js
apps/backend/          # FastAPI
packages/schemas/  # Pydantic models (optional, shared)
data/roadmap.json  # base skill catalog
```

---

## Live Roadmap Forge — technical spec

**Position in the flow:** Onboarding pill rounds + editable diagnosis (HAC-8) → **Forge stream timeline-only (HAC-18)** → Animation reveal → **artifact mode** vertical roadmap (HAC-9)

**Why it's the first wow:** shows AI as a visible engine — not a black box, not a decorative chatbot.

### LangGraph — `roadmap_forge_graph`

```python
class SkillGraphState(TypedDict):
    user_id: str
    profile: DiagnosisResponse          # from onboarding
    base_catalog: list[SkillNode]       # roadmap.json
    accumulated_graph: list[UserSkillNode]  # SOURCE OF TRUTH — deterministic merge
    reasoning_log: list[ReasoningEntry] # timeline for UI
    artifacts: list[Artifact]           # resources/decisions found
    iteration: int
    max_iterations: int               # default 3 (guardrail hackathon)
    status: Literal["running", "done", "error"]
```

### Nodes

| Node | Responsibility | Stream? |
|------|------------------|---------|
| `load_topics` | Loads catalog + profile from Postgres | `step_complete` event |
| `analyze_gaps` | LLM compares profile vs catalog; identifies gaps/redundancies | `reasoning_delta` (token stream) |
| `research_enrich` | OpenAI native `web_search` via LangChain content blocks; enriches priorities/resources with official sources | `artifact_found`, `reasoning_delta` |
| `plan_study_graph` | Planner LLM creates `StudyPlan` with strategy, tasks, evidence, and resources | `artifact_found` |
| `evaluate_plan` | Mini evaluator reviews gaps; if `revise`, feedback returns to the planner with full state | `artifact_found`, `reasoning_delta` |
| `accumulate_graph` | **Python code** merges nodes (status, mastery, priority) — does NOT trust the LLM | `node_updated` per node |
| `should_continue` | Conditional edge: iteration < max AND significant gaps | — |
| `emit_final` | Persists `user_skill_nodes` + emits `graph_ready` | `graph_ready` |

### Golden rule: the LLM proposes, the code disposes

The LLM returns structured JSON (`GraphPatch`), e.g.:
```json
{
  "patches": [
    { "node_id": "http-basics", "status": "recomendado", "mastery_estimated": 42, "priority": "high", "rationale": "..." },
    { "node_id": "git-github", "status": "aprovado", "mastery_estimated": 78, "priority": "low", "rationale": "quick review" }
  ],
  "continue_research": true,
  "summary": "..."
}
```

The `accumulate_graph` node applies patches with Pydantic validation + prerequisite rules.

### SSE — FastAPI endpoint

```
POST /forge
→ 202 { "run_id": "..." }

GET /forge/{run_id}/stream
→ text/event-stream
```

Events (`RoadmapForgeEvent`):
```typescript
type RoadmapForgeEvent =
  | { type: "reasoning_delta"; text: string; step: string }
  | { type: "artifact_found"; label: string; detail: string; sources?: ResearchSource[] }
  | { type: "node_updated"; node: UserSkillNodePartial }
  | { type: "step_complete"; step: string; iteration: number }
  | { type: "graph_ready"; graph: UserSkillNode[] }
  | { type: "error"; message: string };
```

`ResearchSource` comes from citations in LangChain's `AIMessage.content_blocks`, not from manual HTTP to external search APIs. Queries stay internal to the planner/research state; the UI renders a summary + reference cards.

HAC-54 starts the quality loop: the planner receives learner context + sources; the evaluator returns `ship|revise`; on `revise`, the planner receives `previous_plan + evaluator_feedback + research_state + learner_context` for a new iteration before `graph_ready`. HAC-55 persists the approved `StudyPlan` as dynamic nodes (`user_skill_nodes` + generated `skill_nodes`) with `tasks[]`, `references[]`, and prerequisites for post-forge reload.

Implementation: `GraphExecutor` with `astream_events` v2 + normalization in `ai/streaming/events.py`.

### Frontend — UX (HAC-21 + HAC-25)

**Phase 1 — Forge (live):**
- **Timeline only** — full-width numbered steps (`reasoning_delta`, `artifact_found`, `decision`)
- **No graph/map preview** during stream — `node_updated` updates backend state only
- Subtle loading pulse, no generic spinner as the primary UX

**Phase 2 — Reveal:**
- Stream ends with `graph_ready`
- Animation: stream items **fly** to positions in the vertical roadmap layout (spine left/right)
- Transition to `/roadmap` in **`artifact` mode** (no stepper, no progress sidebar)

**Phase 3 — Steady state (HAC-9):**
- Uniform vertical canvas; click node → drawer (references + Ask AI + validate)
- Status/mastery in the drawer, not cluttering the canvas cards

**Demo fallback:** replay JSON of recorded events (seed Ana) if the LLM fails live.

### LangSmith

- 1 trace per `run_id`
- Tags: `roadmap_forge`, `iteration:N`, `user:demo-ana`
- Show in the pitch: "every graph decision is traceable"

---

## Hackathon guardrails

1. **Max 3 iterations** in the loop — avoids runaway
2. **60s timeout** on the total stream
3. **Fixed catalog** — the LLM personalizes, does not invent new nodes in the MVP
4. **Replay fallback** — pre-recorded events for the demo
5. **Research node** — in the MVP it can be LLM-only (no real web search); label it as "research" in the timeline regardless

---

## Linear dependencies

```
HAC-5 (stack) → HAC-6, HAC-7
HAC-8 (onboarding) + HAC-6 + HAC-7 → HAC-18 (Live Roadmap Forge)
HAC-18 → HAC-9 (Skill Graph UI reveal)
HAC-9 + HAC-7 → HAC-10 (Mastery Validation)
```

---

Canonical overview for full runtime/API map: [CHECKPOINT.md](./CHECKPOINT.md).
