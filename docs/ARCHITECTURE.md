# Arquitetura — Career Forge (backend)

> **Para o reviewer:** este documento mostra a arquitetura do backend **depois** do
> ciclo de refactor pós-entrega (HAC-73 … HAC-85). Todos os diagramas são
> [Mermaid](https://mermaid.js.org/) — o GitHub **renderiza nativamente** ao abrir
> este `.md` (sem plugin). Se algum diagrama aparecer como código, recarregue a
> página; o GitHub às vezes faz cache do render.

Camadas: **API** (rotas finas, só transporte) → **Services** (orquestração +
domínio) → **AI** (executor/factory/registry + graphs/agents/tools/llm) → **DB**.
Kernel compartilhado: `schemas/` + `errors.py` (erros de domínio).

---

## Padrões de execução

Existem **três** formas de uma rota chegar no resultado. Saber qual é cada uma
torna os diagramas de sequência muito mais fáceis de ler.

| Padrão | Quando | Caminho |
|--------|--------|---------|
| **executor-collect** | resultado único (sem stream) | rota → `GraphExecutor.execute(stream=False)` → `AgentFactory` → runnable → `unwrap_graph_output` |
| **executor-stream** | streaming SSE | rota → `GraphExecutor.execute(stream=True)` → gera eventos SSE |
| **service-direto** | sem grafo / lógica determinística | rota → service (sem executor) |

| Feature | Padrão |
|---------|--------|
| Diagnosis (multi-turn CTRR) | service-direto (streaming próprio) |
| Live Roadmap Forge | executor-stream |
| Roadmap (steady-state / toggle) | service-direto |
| Validation | executor-collect (via `assessment_flow`) |
| Mock Interview (MCQ) | service-direto p/ scoring + executor p/ open-text legado |
| Mentor | executor-collect (agent embrulha service) |
| Tutor | executor-collect (agent embrulha service) |
| Mentor Report | service-direto |
| Knowledge Gaps / Remediação | background task (fire-and-forget) |

---

## Diagrama de dependência (módulos pós-refactor)

```mermaid
graph TD
  subgraph API["API — rotas finas: transporte + mapeia erro para HTTP"]
    A_diag[diagnosis_interview]
    A_forge[forge]
    A_road[roadmap]
    A_val[validation]
    A_mock[mock_interview]
    A_mentor[mentor]
    A_tutor[tutor]
    A_rep[mentor_report]
  end

  subgraph SVC["Services — orquestracao + dominio"]
    S_flow["assessment_flow"]
    S_persist["assessment_persistence"]
    S_rubric["assessment_rubric"]
    S_val[validation]
    S_mock[mock_interview]
    S_mockctx[mock_interview_context]
    S_sess[mock_interview_session]
    S_plan[planning]
    S_mentor[mentor]
    S_rep[mentor_report]
    S_tutor[tutor]
    S_gaps[knowledge_gaps]
    S_prof[profile_diagnosis]
    S_dsess[diagnosis_session]
    subgraph ROAD["roadmap/ pacote com facade"]
      R_init["__init__ facade"]
      R_cat[catalog]
      R_asm[assembler]
      R_repo[repository]
      R_cmd[commands]
      R_ev["evidence envelope + read_evidence"]
    end
  end

  subgraph AICORE["AI nucleo de execucao"]
    X_exec["executor GraphExecutor"]
    X_fac["factory AgentFactory"]
    X_reg["registry GRAPH_BUILDERS"]
    X_run["run GraphRun + unwrap_graph_output"]
  end
  subgraph AIWORK["AI graphs / agents / tools / llm"]
    G["graphs: validation, mock_interview, roadmap_forge, diagnosis"]
    AG["agents: mentor, tutor"]
    TOOL["tools: mcq, gap_classifier, planner, evaluator, tutor_llm, web_search"]
    LLM["llm: StructuredLlmClient, StructuredToolClient"]
  end

  subgraph DATA["DB + kernel"]
    D_repo["repositories/user"]
    D_mod[models]
    D_sess[session]
    K_err["errors DomainError"]
    K_sch[schemas]
  end

  A_val --> S_flow
  A_mock --> S_flow
  A_road --> R_init
  A_rep --> S_rep
  A_diag --> S_dsess
  A_mentor --> X_exec
  A_tutor --> X_exec
  A_forge --> X_exec
  A_mentor --> S_mentor
  A_tutor --> S_tutor

  S_flow --> S_persist
  S_flow --> S_plan
  S_flow --> X_exec
  S_persist --> R_init
  S_persist --> D_repo
  S_val --> S_rubric
  S_val --> R_init
  S_mock --> S_rubric
  S_mock --> S_sess
  S_mockctx --> R_init
  S_plan --> R_init
  S_mentor --> R_init
  S_mentor --> S_gaps
  S_rep --> R_init
  S_gaps --> R_ev
  S_gaps --> D_repo
  S_gaps --> TOOL
  S_dsess --> LLM
  S_tutor --> TOOL

  R_init --> R_cat
  R_init --> R_asm
  R_init --> R_repo
  R_init --> R_cmd
  R_init --> R_ev
  R_cmd --> R_asm
  R_cmd --> R_repo
  R_asm --> R_ev
  R_asm --> R_cat
  R_repo --> R_cat

  X_exec --> X_fac
  X_fac --> X_reg
  X_reg --> G
  X_reg --> AG
  X_exec --> X_run
  AG --> S_mentor
  AG --> S_tutor
  G --> S_rubric
  G --> TOOL
  TOOL --> LLM

  SVC --> D_repo
  SVC --> K_err
  SVC --> K_sch
```

**Regra de direção (o que o refactor fixou):** `API → Services → DB/kernel`.
O HAC-77 removeu a inversão **services → ai/graphs**. A única dependência "para
cima" sancionada é **graphs/agents → services** (os runnables são finos e
embrulham o domínio determinístico). `catalog` e `evidence` são folhas (sem
dependências internas no pacote `roadmap/`).

---

## Sequência — Diagnosis Interview (multi-turn CTRR)

`service-direto` — não passa pelo `GraphExecutor`; tem streaming próprio.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant R as api diagnosis_interview
  participant SS as diagnosis_session
  participant CV as services cv
  participant LLM as diagnosis LLM
  participant DB as Postgres

  FE->>R: POST /diagnosis/interview/start
  R->>SS: start_interview(body)
  opt tem CV
    SS->>CV: parse_cv_attachment / attach_extracted_text
  end
  SS->>LLM: initialize_belief(intake, cv)
  SS->>LLM: plan_questions(belief)
  SS->>DB: persist diagnosis_session
  SS-->>FE: round 1 perguntas CTRR

  loop ate belief fechar ou max rounds
    FE->>R: POST /interview/{id}/turn
    R->>SS: submit_turn(id, answers)
    SS->>LLM: update_belief(transcript, answers)
    alt ainda aberto
      SS->>LLM: plan_questions(belief)
      SS-->>FE: proximo round
    else fechado
      SS->>LLM: finalize_diagnosis(belief)
      SS->>DB: persist final
      SS-->>FE: DiagnosisResponse
    end
  end

  FE->>R: POST /diagnosis/confirm
  R->>SS: profile_diagnosis.confirm_diagnosis
  SS->>DB: grava Profile motor-input
```

---

## Sequência — Live Roadmap Forge

`executor-stream` — POST cria o run (pending), o GET consome o SSE.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant R as api forge
  participant PD as profile_diagnosis
  participant EX as GraphExecutor
  participant GF as graph roadmap_forge
  participant TL as forge tools
  participant FP as forge_persistence
  participant CMD as roadmap commands
  participant DB as Postgres

  FE->>R: POST /forge
  R->>PD: load_forge_motor_input(user_id)
  PD-->>R: motor input ou ProfileNotFoundError 404
  R->>DB: store GraphRun roadmap_forge pending
  R-->>FE: 202 run_id

  FE->>R: GET /forge/{run_id}/stream
  R->>EX: execute(run, stream=true)
  EX->>GF: astream_events v2
  loop research, plan, evaluate, revise
    GF->>TL: web_search / planner / evaluator
    GF-->>FE: SSE reasoning, artifact, node_updated
  end
  GF-->>EX: graph_ready grafo final
  EX-->>FE: SSE graph_ready
  R->>FP: persist_graph_ready(graph)
  FP->>CMD: sync_user_graph(nodes)
  CMD->>DB: upsert user_skill_nodes evidence canonico
```

---

## Sequência — Roadmap (steady-state + checklist toggle)

`service-direto` — através do pacote `roadmap/`.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant R as api roadmap
  participant CMD as roadmap commands
  participant CAT as roadmap catalog
  participant REPO as roadmap repository
  participant ASM as roadmap assembler
  participant EV as roadmap evidence
  participant DB as Postgres

  FE->>R: GET /roadmap
  R->>CMD: get_user_roadmap
  CMD->>CAT: load_roadmap_catalog
  CMD->>REPO: _user_state_map
  REPO->>DB: SELECT user_skill_nodes
  CMD->>ASM: _merge_node(catalog, row)
  ASM->>EV: read_evidence(row.evidence)
  EV-->>ASM: envelope checklist + remediation viram tasks
  CMD-->>FE: RoadmapResponse

  FE->>R: PATCH /roadmap/nodes/{id}/checklist
  R->>CMD: toggle_checklist_item
  alt node inexistente
    CMD-->>R: NodeNotFoundError
    R-->>FE: 404
  else item inexistente
    CMD-->>R: ChecklistItemNotFoundError
    R-->>FE: 400
  else ok
    CMD->>DB: update checklist_progress
    CMD-->>FE: RoadmapResponse
  end
```

---

## Sequência — Validation

`executor-collect` orquestrado por `assessment_flow`.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant R as api validation
  participant AF as assessment_flow
  participant SV as services validation
  participant EX as GraphExecutor
  participant GV as graph validation
  participant RUB as assessment_rubric
  participant AP as assessment_persistence
  participant PL as planning
  participant DB as Postgres

  FE->>R: POST /validation
  R->>AF: run_validation(body)
  AF->>SV: build_validation_questions backfill rubric
  AF->>EX: execute(validation, collect)
  EX->>GV: astream_events
  GV->>RUB: score_answer / keywords_for
  GV-->>EX: graph_complete ValidationResponse
  EX-->>AF: unwrap_graph_output
  AF->>AP: persist_assessment_result
  AP->>DB: upsert UserSkillNode + Validation evidence canonico
  AF->>PL: recalibrate_after_validation
  PL->>DB: sync_user_graph GraphPatch aplicado
  AF-->>FE: validation, node_status, graph_patch, roadmap
```

---

## Sequência — Mock Interview MCQ (+ loop de gaps e remediação)

`service-direto` para scoring determinístico + background fire-and-forget.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant R as api mock_interview
  participant AF as assessment_flow
  participant MC as mock_interview_context
  participant MCQ as tool mcq
  participant SESS as mock_interview_session
  participant SM as services mock_interview
  participant AP as assessment_persistence
  participant BG as knowledge_gaps background
  participant GC as tool gap_classifier
  participant DB as Postgres

  FE->>R: GET /mock-interview/questions
  R->>MC: build_mock_interview_context
  R->>MCQ: generate_mcq StructuredToolClient ou fallback
  MCQ->>SESS: save session gabarito in-memory
  R-->>FE: MCQ sem correct_option

  FE->>R: POST /mock-interview session_id + answers
  R->>AF: run_mock_interview
  AF->>SM: evaluate_mcq_session gabarito deterministico
  AF->>AP: persist_assessment_result mock_interview=true
  AP->>DB: upsert evidence canonico
  AF->>BG: add_task classify_and_store_gaps fire-and-forget
  AF-->>FE: validation, node_status, roadmap
  Note over BG,DB: pos-resposta em background
  BG->>GC: classify_gaps LLM ou fallback
  BG->>DB: upsert KnowledgeGap ledger
  BG->>DB: sync_remediation_tasks grava evidence.remediation
```

---

## Sequência — Mentor

`executor-collect` — o agent embrulha o service determinístico.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant R as api mentor
  participant SM as services mentor
  participant KG as knowledge_gaps
  participant EX as GraphExecutor
  participant AG as agent mentor
  participant DB as Postgres

  FE->>R: POST /mentor
  R->>SM: load_mentor_context(user, node)
  SM->>DB: validations + user_skill_nodes read_evidence
  SM->>KG: list_open_gaps ledger primario
  R->>EX: execute(mentor, collect) com context_snapshot
  EX->>AG: astream_events
  AG->>SM: build_mentor_response intent dispatch
  AG-->>EX: graph_complete MentorResponse
  EX-->>R: unwrap_graph_output
  R-->>FE: reply, references, context_snapshot
```

---

## Sequência — Tutor (Q&A do capítulo)

`executor-collect` — o agent embrulha o service.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant R as api tutor
  participant ST as services tutor
  participant EX as GraphExecutor
  participant AG as agent tutor
  participant TL as tool tutor_llm
  participant DB as Postgres

  FE->>R: POST /tutor
  R->>ST: load_tutor_context key_concepts + refs + open_gaps
  ST->>DB: skill node + gaps
  R->>EX: execute(tutor, collect) com context_snapshot
  EX->>AG: astream_events
  AG->>ST: build_tutor_response(payload, context)
  ST->>TL: generate_tutor_reply StructuredToolClient ou fallback
  AG-->>EX: graph_complete TutorResponse
  EX-->>R: unwrap_graph_output
  R-->>FE: reply, used_concepts
```

---

## Sequência — Mentor Report

`service-direto` — agrega histórico de validações.

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant R as api mentor_report
  participant MR as mentor_report
  participant EV as roadmap evidence
  participant PD as profile_diagnosis
  participant DB as Postgres

  FE->>R: GET /mentor-report
  R->>MR: get_mentor_report
  MR->>DB: Profile + validations + user_skill_nodes
  MR->>PD: diagnosis_response_from_profile parse v2
  loop por validacao
    MR->>EV: read_evidence(row) validation_summary
  end
  MR-->>FE: relatorio agregado strengths/gaps por no
```

---

## Decisões arquiteturais (pontos de revisão)

1. **`ai/graphs` e `ai/agents` dependem de `services`** (runnables embrulham o
   domínio determinístico). É a única dependência "para cima". Alternativa:
   mover a lógica determinística (rubric/mentor/tutor) para um pacote `domain/`
   neutro. Mantido como está — runnables finos e previsíveis.
2. **Dois clients LLM**: `StructuredLlmClient` (async, diagnosis) e
   `StructuredToolClient` (sync, tools). Unificar num só com `invoke`/`ainvoke`
   seria mais limpo (ficou fora do escopo do HAC-82).
3. **Diagnosis tem dois caminhos**: o multi-turn real (`diagnosis_session`,
   service-direto) + um `diagnosis` graph legado via executor
   (`api/diagnosis.create_diagnosis`) que o front não usa mais → candidato a
   remoção de dead-code.
4. **Sessão MCQ é in-memory** (`mock_interview_session`): o gabarito não
   persiste. Simples e suficiente para o fluxo, mas é estado efêmero (perde em
   restart / múltiplas instâncias).
5. **Evidence normalizado (HAC-85)**: um envelope canônico
   `{checklist, validation, remediation, metadata}` + `read_evidence` como único
   adapter de leitura do legado. Escrita só no shape novo; migração **lazy** (sem
   rewrite em massa). Remediação numa chave dedicada, desacoplada do checklist.
6. **`assessment_flow` mantém `except Exception` amplo** no persist/recalibrate
   (resiliência herdada das rotas) — preservado para não mudar comportamento;
   poderia virar fail-fast.

---

## Documentos relacionados

- [docs/engineering/EXECUTION-FLOW.md](./engineering/EXECUTION-FLOW.md) — árvore E2E + ordem de dispatch
- [docs/engineering/AI-EXECUTION.md](./engineering/AI-EXECUTION.md) — GraphRun, GraphExecutor, AgentFactory
- [docs/engineering/REPO-STRUCTURE.md](./engineering/REPO-STRUCTURE.md) — layout de pastas
- [docs/CHECKPOINT.md](./CHECKPOINT.md) — overview de produto + stack
