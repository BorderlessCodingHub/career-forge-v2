# Stack fechada + Live Roadmap Forge

## Stack oficial

| Camada | Tecnologia |
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
packages/schemas/  # Pydantic models (opcional shared)
data/roadmap.json  # catálogo base de skills
```

---

## Live Roadmap Forge — spec técnica

**Posição no fluxo:** Onboarding pill rounds + editable diagnosis (HAC-8) → **Forge stream timeline-only (HAC-18)** → Animation reveal → **artifact mode** vertical roadmap (HAC-9)

**Por que é o primeiro wow:** mostra IA como motor visível — não black box, não chatbot decorativo.

### LangGraph — `roadmap_forge_graph`

```python
class SkillGraphState(TypedDict):
    user_id: str
    profile: DiagnosisResponse          # do onboarding
    base_catalog: list[SkillNode]       # roadmap.json
    accumulated_graph: list[UserSkillNode]  # SOURCE OF TRUTH — merge determinístico
    reasoning_log: list[ReasoningEntry] # timeline para UI
    artifacts: list[Artifact]           # resources/decisões encontradas
    iteration: int
    max_iterations: int               # default 3 (guardrail hackathon)
    status: Literal["running", "done", "error"]
```

### Nodes

| Node | Responsabilidade | Stream? |
|------|------------------|---------|
| `load_topics` | Carrega catálogo + perfil do Postgres | evento `step_complete` |
| `analyze_gaps` | LLM compara perfil vs catálogo; identifica lacunas/redundâncias | `reasoning_delta` (token stream) |
| `research_enrich` | OpenAI native `web_search` via LangChain content blocks; enriquece prioridades/recursos com fontes oficiais | `artifact_found`, `reasoning_delta` |
| `plan_study_graph` | Planner LLM cria `StudyPlan` com estratégia, tarefas, evidências e recursos | `artifact_found` |
| `evaluate_plan` | Evaluator mini revisa gaps; se `revise`, feedback volta ao planner com estado completo | `artifact_found`, `reasoning_delta` |
| `accumulate_graph` | **Código Python** merge nodes (status, mastery, priority) — NÃO confia na LLM | `node_updated` por nó |
| `should_continue` | Conditional edge: iteration < max AND gaps significativos | — |
| `emit_final` | Persiste `user_skill_nodes` + emite `graph_ready` | `graph_ready` |

### Regra de ouro: LLM propõe, código dispõe

A LLM retorna JSON estruturado (`GraphPatch`), ex.:
```json
{
  "patches": [
    { "node_id": "http-basics", "status": "recomendado", "mastery_estimated": 42, "priority": "high", "rationale": "..." },
    { "node_id": "git-github", "status": "aprovado", "mastery_estimated": 78, "priority": "low", "rationale": "revisão rápida" }
  ],
  "continue_research": true,
  "summary": "..."
}
```

Node `accumulate_graph` aplica patches com validação Pydantic + regras de prerequisite.

### SSE — FastAPI endpoint

```
POST /forge
→ 202 { "run_id": "..." }

GET /forge/{run_id}/stream
→ text/event-stream
```

Eventos (`RoadmapForgeEvent`):
```typescript
type RoadmapForgeEvent =
  | { type: "reasoning_delta"; text: string; step: string }
  | { type: "artifact_found"; label: string; detail: string; sources?: ResearchSource[] }
  | { type: "node_updated"; node: UserSkillNodePartial }
  | { type: "step_complete"; step: string; iteration: number }
  | { type: "graph_ready"; graph: UserSkillNode[] }
  | { type: "error"; message: string };
```

`ResearchSource` vem de citações nos `AIMessage.content_blocks` do LangChain, não de HTTP manual para search APIs externas. Queries ficam internas ao planner/research state; a UI renderiza resumo + cards de referência.

HAC-54 inicia o loop de qualidade: o planner recebe contexto do aluno + fontes; o evaluator retorna `ship|revise`; em caso de `revise`, o planner recebe `previous_plan + evaluator_feedback + research_state + learner_context` para uma nova iteração antes de `graph_ready`.

Implementação: `GraphExecutor` com `astream_events` v2 + normalização em `ai/streaming/events.py`.

### Frontend — UX (HAC-21 + HAC-25)

**Fase 1 — Forge (live):**
- **Timeline only** — full-width numbered steps (`reasoning_delta`, `artifact_found`, `decision`)
- **No graph/map preview** during stream — `node_updated` updates backend state only
- Loading pulse suave, sem spinner genérico como UX primária

**Fase 2 — Reveal:**
- Stream encerra com `graph_ready`
- Animação: itens do stream **voam** para posições no layout vertical roadmap (spine left/right)
- Transição para `/roadmap` em **`artifact` mode** (sem stepper, sem sidebar de progresso)

**Fase 3 — Steady state (HAC-9):**
- Canvas vertical uniforme; click node → drawer (referências + Ask AI + validar)
- Status/mastery no drawer, não poluindo cards do canvas

**Fallback demo:** replay JSON de eventos gravados (seed Ana) se LLM falhar ao vivo.

### LangSmith

- 1 trace por `run_id`
- Tags: `roadmap_forge`, `iteration:N`, `user:demo-ana`
- Mostrar no pitch: "cada decisão do grafo é rastreável"

---

## Guardrails hackathon

1. **Max 3 iterations** no loop — evita runaway
2. **Timeout 60s** no stream total
3. **Catálogo fixo** — LLM personaliza, não inventa nós novos no MVP
4. **Replay fallback** — eventos pré-gravados para demo
5. **Research node** — no MVP pode ser LLM-only (sem web search real); label como "research" na timeline mesmo assim

---

## Dependências Linear

```
HAC-5 (stack) → HAC-6, HAC-7
HAC-8 (onboarding) + HAC-6 + HAC-7 → HAC-18 (Live Roadmap Forge)
HAC-18 → HAC-9 (Skill Graph UI reveal)
HAC-9 + HAC-7 → HAC-10 (Mastery Validation)
```

---

Canonical overview for full runtime/API map: [CHECKPOINT.md](./CHECKPOINT.md).
