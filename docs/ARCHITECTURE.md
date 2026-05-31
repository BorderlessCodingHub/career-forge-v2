# Architecture — Career Forge (backend)

> **For the reviewer:** this document shows the backend architecture **after** the
> post-delivery refactor cycle (HAC-73 … HAC-85). All diagrams are
> [Mermaid](https://mermaid.js.org/) — GitHub **renders them natively** when you open
> this `.md` (no plugin). If a diagram shows up as code, reload the
> page; GitHub sometimes caches the render.

Layers: **API** (thin routes, transport only) → **Services** (orchestration +
domain) → **AI** (executor/factory/registry + graphs/agents/tools/llm) → **DB**.
Shared kernel: `schemas/` + `errors.py` (domain errors).

---

## Execution patterns

There are **three** ways a route reaches its result. Knowing which is which
makes the sequence diagrams much easier to read.

| Pattern | When | Path |
|--------|--------|---------|
| **executor-collect** | single result (no stream) | route → `GraphExecutor.execute(stream=False)` → `AgentFactory` → runnable → `unwrap_graph_output` |
| **executor-stream** | SSE streaming | route → `GraphExecutor.execute(stream=True)` → emits SSE events |
| **service-direto** | no graph / deterministic logic | route → service (no executor) |

| Feature | Pattern |
|---------|--------|
| Diagnosis (multi-turn CTRR) | service-direto (own streaming) |
| Live Roadmap Forge | executor-stream |
| Roadmap (steady-state / toggle) | service-direto |
| Validation | executor-collect (via `assessment_flow`) |
| Mock Interview (MCQ) | service-direto for scoring + executor for legacy open-text |
| Mentor | executor-collect (agent wraps service) |
| Tutor | executor-collect (agent wraps service) |
| Mentor Report | service-direto |
| Knowledge Gaps / Remediation | background task (fire-and-forget) |

---

## Dependency diagram (post-refactor modules)

```mermaid
graph TD
  subgraph API["API — thin routes: transport + map error to HTTP"]
    A_diag[diagnosis_interview]
    A_forge[forge]
    A_road[roadmap]
    A_val[validation]
    A_mock[mock_interview]
    A_mentor[mentor]
    A_tutor[tutor]
    A_rep[mentor_report]
  end

  subgraph SVC["Services — orchestration + domain"]
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
    subgraph ROAD["roadmap/ package with facade"]
      R_init["__init__ facade"]
      R_cat[catalog]
      R_asm[assembler]
      R_repo[repository]
      R_cmd[commands]
      R_ev["evidence envelope + read_evidence"]
    end
  end

  subgraph AICORE["AI execution core"]
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

**Direction rule (what the refactor locked in):** `API → Services → DB/kernel`.
HAC-77 removed the **services → ai/graphs** inversion. The only sanctioned "upward"
dependency is **graphs/agents → services** (the runnables are thin and
wrap the deterministic domain). `catalog` and `evidence` are leaves (no
internal dependencies within the `roadmap/` package).

---

## Sequence — Diagnosis Interview (multi-turn CTRR)

`service-direto` — does not go through `GraphExecutor`; it has its own streaming.

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
  opt has CV
    SS->>CV: parse_cv_attachment / attach_extracted_text
  end
  SS->>LLM: initialize_belief(intake, cv)
  SS->>LLM: plan_questions(belief)
  SS->>DB: persist diagnosis_session
  SS-->>FE: round 1 CTRR questions

  loop until belief closes or max rounds
    FE->>R: POST /interview/{id}/turn
    R->>SS: submit_turn(id, answers)
    SS->>LLM: update_belief(transcript, answers)
    alt still open
      SS->>LLM: plan_questions(belief)
      SS-->>FE: next round
    else closed
      SS->>LLM: finalize_diagnosis(belief)
      SS->>DB: persist final
      SS-->>FE: DiagnosisResponse
    end
  end

  FE->>R: POST /diagnosis/confirm
  R->>SS: profile_diagnosis.confirm_diagnosis
  SS->>DB: write Profile motor-input
```

---

## Sequence — Live Roadmap Forge

`executor-stream` — POST creates the run (pending), GET consumes the SSE.

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
  PD-->>R: motor input or ProfileNotFoundError 404
  R->>DB: store GraphRun roadmap_forge pending
  R-->>FE: 202 run_id

  FE->>R: GET /forge/{run_id}/stream
  R->>EX: execute(run, stream=true)
  EX->>GF: astream_events v2
  loop research, plan, evaluate, revise
    GF->>TL: web_search / planner / evaluator
    GF-->>FE: SSE reasoning, artifact, node_updated
  end
  GF-->>EX: graph_ready final graph
  EX-->>FE: SSE graph_ready
  R->>FP: persist_graph_ready(graph)
  FP->>CMD: sync_user_graph(nodes)
  CMD->>DB: upsert user_skill_nodes canonical evidence
```

---

## Sequence — Roadmap (steady-state + checklist toggle)

`service-direto` — through the `roadmap/` package.

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
  EV-->>ASM: envelope checklist + remediation become tasks
  CMD-->>FE: RoadmapResponse

  FE->>R: PATCH /roadmap/nodes/{id}/checklist
  R->>CMD: toggle_checklist_item
  alt node does not exist
    CMD-->>R: NodeNotFoundError
    R-->>FE: 404
  else item does not exist
    CMD-->>R: ChecklistItemNotFoundError
    R-->>FE: 400
  else ok
    CMD->>DB: update checklist_progress
    CMD-->>FE: RoadmapResponse
  end
```

---

## Sequence — Validation

`executor-collect` orchestrated by `assessment_flow`.

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
  AP->>DB: upsert UserSkillNode + Validation canonical evidence
  AF->>PL: recalibrate_after_validation
  PL->>DB: sync_user_graph GraphPatch applied
  AF-->>FE: validation, node_status, graph_patch, roadmap
```

---

## Sequence — Mock Interview MCQ (+ gaps and remediation loop)

`service-direto` for deterministic scoring + fire-and-forget background.

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
  R->>MCQ: generate_mcq StructuredToolClient or fallback
  MCQ->>SESS: save session answer-key in-memory
  R-->>FE: MCQ without correct_option

  FE->>R: POST /mock-interview session_id + answers
  R->>AF: run_mock_interview
  AF->>SM: evaluate_mcq_session deterministic answer-key
  AF->>AP: persist_assessment_result mock_interview=true
  AP->>DB: upsert canonical evidence
  AF->>BG: add_task classify_and_store_gaps fire-and-forget
  AF-->>FE: validation, node_status, roadmap
  Note over BG,DB: post-answer in background
  BG->>GC: classify_gaps LLM or fallback
  BG->>DB: upsert KnowledgeGap ledger
  BG->>DB: sync_remediation_tasks write evidence.remediation
```

---

## Sequence — Mentor

`executor-collect` — the agent wraps the deterministic service.

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
  SM->>KG: list_open_gaps primary ledger
  R->>EX: execute(mentor, collect) with context_snapshot
  EX->>AG: astream_events
  AG->>SM: build_mentor_response intent dispatch
  AG-->>EX: graph_complete MentorResponse
  EX-->>R: unwrap_graph_output
  R-->>FE: reply, references, context_snapshot
```

---

## Sequence — Tutor (chapter Q&A)

`executor-collect` — the agent wraps the service.

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
  R->>EX: execute(tutor, collect) with context_snapshot
  EX->>AG: astream_events
  AG->>ST: build_tutor_response(payload, context)
  ST->>TL: generate_tutor_reply StructuredToolClient or fallback
  AG-->>EX: graph_complete TutorResponse
  EX-->>R: unwrap_graph_output
  R-->>FE: reply, used_concepts
```

---

## Sequence — Mentor Report

`service-direto` — aggregates validation history.

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
  loop per validation
    MR->>EV: read_evidence(row) validation_summary
  end
  MR-->>FE: aggregated report strengths/gaps per node
```

---

## Architectural decisions (review points)

1. **`ai/graphs` and `ai/agents` depend on `services`** (runnables wrap the
   deterministic domain). It is the only "upward" dependency. Alternative:
   move the deterministic logic (rubric/mentor/tutor) into a neutral `domain/`
   package. Kept as is — thin, predictable runnables.
2. **Two LLM clients**: `StructuredLlmClient` (async, diagnosis) and
   `StructuredToolClient` (sync, tools). Unifying them into one with `invoke`/`ainvoke`
   would be cleaner (it was out of scope for HAC-82).
3. **Diagnosis has two paths**: the real multi-turn one (`diagnosis_session`,
   service-direto) + a legacy `diagnosis` graph via the executor
   (`api/diagnosis.create_diagnosis`) that the frontend no longer uses → candidate for
   dead-code removal.
4. **MCQ session is in-memory** (`mock_interview_session`): the answer key is not
   persisted. Simple and sufficient for the flow, but it is ephemeral state (lost on
   restart / multiple instances).
5. **Normalized evidence (HAC-85)**: a canonical envelope
   `{checklist, validation, remediation, metadata}` + `read_evidence` as the single
   read adapter for the legacy format. Writes only in the new shape; **lazy** migration (no
   mass rewrite). Remediation in a dedicated key, decoupled from the checklist.
6. **`assessment_flow` keeps a broad `except Exception`** in persist/recalibrate
   (resilience inherited from the routes) — preserved to avoid changing behavior;
   could become fail-fast.

---

## Related documents

- [docs/engineering/EXECUTION-FLOW.md](./engineering/EXECUTION-FLOW.md) — E2E tree + dispatch order
- [docs/engineering/AI-EXECUTION.md](./engineering/AI-EXECUTION.md) — GraphRun, GraphExecutor, AgentFactory
- [docs/engineering/REPO-STRUCTURE.md](./engineering/REPO-STRUCTURE.md) — folder layout
- [docs/CHECKPOINT.md](./CHECKPOINT.md) — product + stack overview
