# Career Forge v2 — Plano de Execução

> Borderless · labs.borderlesscoding.com/career-forge  
> Executor: Pedro Alano  
> Prazo estimado: 4–5 semanas ·  
> **Atualizado:** 2026-08-08 — F3 grill (F3a/F3b); prior 2026-07-30 ADR-003; 2026-07-25 F2 grill; 2026-07-20 Yuri

---

## Visão

Career Forge v2 reposiciona o motor AI-native de aprendizado para **LLM engineers**: 4 goals especializados, prompts calibrados para o espectro BASE/PSP (6 meses → 40 anos de XP), english-first, e rebrand Borderless. O motor LangGraph (diagnóstico CTRR → forge → validação) permanece intocado.

**Não é redesign.** É reposicionamento de goals, prompts, catálogo e identidade visual.

**Público:** somente alunos BASE e PSP.

---

## Decision log (travado)

| # | Decisão |
|---|--------|
| 1 | Auth **issuer** via `borderless-api` (platform) — **F3b** ([CAR-28](https://linear.app/career-forge-v2/issue/CAR-28)). **Amend 2026-07-30:** scaffold F3-ready (`AuthProvider` + Bearer JWT anon) ships **before** F3 per [ADR-003](./decisions/ADR-003-forge-recovery-auth-scaffold.md). **Amend 2026-08-08:** pilots (F3a) do **not** require platform login. Magic link local: fora. |
| 2 | Hard stop API: **R$500/mês** (pool global). **R$700** = teto de *aprovação* do gate F1 (não o kill-switch). |
| 3 | Throttle: **pool global R$500** + **cap por usuário** — F3.2 lock: **`FORGE_CAP_PER_USER_MONTH=2`**; kill-switch P95 **`COST_P95_BRL_PER_RUN=1.3639`** (F2 re-cost). |
| 4 | Funil único (4 goals); barra de passagem por **evidência CTRR**, não por anos de XP. |
| 5 | “Não passa” no diagnóstico = **soft gate** no piloto (forge lean + aviso). Hard block = v2.1 após calibrar nota. |
| 6 | Output bom = LEAN com fit ≥70% dos **must-have nodes** derivados de corpus de vagas. **QA humano**, não RAG de jobs no produto v2. |
| 7 | Kill-switch runtime = **GraphRuns × P95 BRL** medido no gate F1 (+ buffer ~10%). LangSmith audita. |
| 8 | Pool conta **toda GraphRun billable** (diagnosis, forge, validation, mentor). Demo-ana + sintéticos do gate: fora do pool de aluno, dentro do relatório F1. |
| 9 | Primeiro humano BASE/PSP: **somente na F3** (após gate + golden cases). **Amend 2026-08-08:** humans need **hard caps + rebrand/landing** (F3a) — **not** Borderless login. F2 100% interno/sintético. |
| 10 | URL: **path** — `labs.borderlesscoding.com/career-forge`. **Amend 2026-08-08:** thin **marketing** on `/career-forge`; product stays at current routes (no `/career-forge/app` migration). Frame depois, mesmo path. |
| 11 | Must-haves: draft Pedro (1 pág/goal) → 1 rodada sign-off Yuri; silêncio = baseline. |
| 12 | F1 em Track A (desbloqueado) / Track B (nginx path — aguarda Brunno/domínio). Restante de org/deploy Track B já OK. |
| 13 | **Forge recovery (ADR-003):** lista histórica via `forge_artifacts`; deep-links `share` (read-only) + `resume` (single-use/~7d); open = promote snapshot; freeze-before-promote. |
| 14 | **Auth wire:** `Authorization: Bearer`; SSE via **stream ticket**. Paralelo a F2; CAR-21 só bloqueia path Labs do stream. |
| 15 | Email opcional (Slice 2) — store only; send resume = **F3b** (CAR-28). Diagnosis mid-flight fora; diagnosis **result** reutilizável = Slice 2. |

---

## Decisões de design

### Custo de API

- **Hard stop operacional:** R$500/mês pool global (escassez intencional — “virar o mês”)
- **Teto de aprovação do gate F1:** R$700/mês (se P95 × volume projetado > R$700, Yuri não libera piloto)
- **Gate obrigatório (F1):** 20–30 forges sintéticos (+ samples dos outros graphs) via LangSmith → relatório (média + P95 por `graph_name` / goal) → Yuri aprova
- **Nenhum aluno acessa antes da aprovação do gate**
- Kill-switch: proxy `monthly_spend_brl ≈ Σ(runs × p95_brl)` com FX fixo documentado no relatório
- Revisão após 30 dias de uso real

### Controle de custo

- Cap global R$500 (env: `MONTHLY_API_BUDGET_BRL=500`)
- Cap por usuário (env: `FORGE_CAP_PER_USER_MONTH=2` — F3.2)
- Contadores no banco por usuário + agregado mensal de GraphRuns billable
- Monitoramento contínuo via LangSmith

### Autenticação

- **F1/F2 (amend 2026-07-30):** scaffold `AuthProvider` + JWT anon Bearer ([ADR-003](./decisions/ADR-003-forge-recovery-auth-scaffold.md)) — uso interno / recovery / **F3a pilots**
- **F3a:** funnel = marketing CTA → product (anon); entry-gate login deferred
- **F3b:** issuer `borderless-api` no mesmo middleware — validar token → `user_id` estável; last eng slice when issuer ready ([CAR-28](https://linear.app/career-forge-v2/issue/CAR-28))
- SSO/magic link local: fora de escopo v2 (platform é a regra do ecossistema)

### Demo user

- `"demo-ana"` mantido para demonstração na landing
- Não entra no pool de custo por aluno real

### Goals LLM (substituem fullstack/data/ai-ml/web3)

| Goal | Track |
|------|-------|
| `rag-engineer` | Production RAG & Advanced Retrieval |
| `agent-engineer` | Agent Engineering (MCP, Tool Use, Failure Modes) |
| `llm-evals` | LLM Evaluation & Observability (LLMOps) |
| `fine-tuning` | Fine-Tuning & Alignment (LoRA, DPO, Custom Models) |

Seeds mínimos do catálogo adiantados para F1 (necessário para forges sintéticos do gate).

Must-have nodes (8–12/goal) draftados por Pedro a partir de corpus enxuto (~25–40 vagas/goal) → sign-off Yuri.

### CTRR para público BASE/PSP

**CTRR** = brand do loop Judge/Interviewer (prose). Chaves em produção = **5 profile dims** ADR-002 (`motivation_goal`, `background_transfer`, `learning_velocity`, `hands_on_proof`, `constraints`) — já live; **não** migrar schema para Conceptual / Technical / Readiness / Resourcefulness.  
Prompts/rubrics: de “iniciante em transição” → espectro real (early ↔ staff), com perguntas práticas de aplicação e system AI design.

Soft gate: `profile_score = mean(5 dim confidences)` abaixo do cutoff → aviso + forge lean (não bloqueia no piloto). Ver F2.8 / CAR-15 / CAR-18 (cutoff **0.50**).

16 golden cases (4 goals × espectro) = critério de QA da F2.

### English-first

- UI, prompts, catálogo e relatórios em inglês desde a F2
- **F3a (F3.4):** pt-BR = marketing + chrome only; diagnosis/forge/validation AI + prompts stay EN
- Full dual-locale / AI pt-BR: later
- Público PSP/BASE compatível

### Landing page

- **v2 (amend 2026-08-08 / F3.3):** Next.js at Labs `basePath=/career-forge` — thin **marketing** layer on `/`; product routes unchanged (no `/app` prefix)
- Frame: só quando houver comercialização/growth para fora (fora do horizonte atual)
- Demo do forge streaming reutiliza componentes existentes

### Rebrand

- Identidade: #121212 / #5316CC / #44D5AD + brand kit Borderless (aprovado)
- Escopo F3a (F3.5): tokens Tailwind, logo SVG, favicon **+** marketing landing composition — sem redesign estrutural do produto
- Entrega: F3a

### Infra

- Repo na org `borderlesscodinghub` (acesso em andamento / parcial OK)
- Deploy: `labs.borderlesscoding.com/career-forge` no VPS Labs
- **Pendente Track B:** nginx path + apontamento de domínio (Brunno)
- Imagens Docker via GHCR da org · CI/CD GitHub Actions

---

## Fases

### Fase 1 — Infra + gate de custo

**Entrega:** path Labs estável (quando nginx OK) + relatório de custo aprovado por Yuri  

#### Track A — agora (sem depender de domínio)

1. Troca de goals + seeds mínimos (4 tracks LLM)
2. Instrumentação de custo: contadores GraphRun billable, pool global, cap/user via env, proxy P95
3. 20–30 forges sintéticos (+ samples outros graphs) → relatório custo (média + P95, FX documentado)
4. Draft must-haves (1 página/goal) para sign-off Yuri (adianta F2)

#### Track B — quase OK

1. Org / GHCR / Actions — **já OK**
2. Deploy VPS — **já OK** salvo **nginx path** `labs.../career-forge` (aguarda Brunno / apontamento)

**Gate:** relatório custo + budget (hard R$500 / aprovação ≤ R$700) aprovado por Yuri → **nenhum aluno antes disso**

---

### Fase 2 — 4 goals LLM + prompts + english-first

**Entrega:** diagnóstico → forge → validação end-to-end por goal (sintético)  
**Critério de aceite:** golden cases + cobertura ≥70% dos must-haves sign-offados  
**Inclui:** soft gate no diagnóstico; prompts CTRR calibrados; english-first  
**Pré-requisito:** gate F1 aprovado; must-haves com sign-off (ou baseline por silêncio)  
**Sem alunos reais.** Mentor fora de escopo F2.

#### Decisões travadas (grill 2026-07-25)

| # | Decisão |
|---|--------|
| F2.1 | Pedro pontua 16 golden cases com rubric escrita; Yuri spot-check 4 (1/goal) |
| F2.2 | Lean forge = mesmo grafo + mesmo stream UX; só prune (sem pipeline “barato”) |
| F2.3 | English hard cutover em F2; pt-BR só em F3 (sem flag half-i18n) |
| F2.4 | ≥70% = cobertura **pós-forge** dos must-haves nos golden runs (por goal), não inventário do catálogo |
| F2.5 | Uma barra global de soft gate para os 4 goals |
| F2.6 | Pedro autor dos 16 casos sintéticos |
| F2.7 | Soft-gate warning no summary do diagnóstico **e** na entrada do forge |
| F2.8 | Soft gate quando `profile_score = mean(5 dim confidences) < cutoff` (5 live dims ADR-002; cutoff **0.50** via `SOFT_GATE_CUTOFF` — CAR-18 midpoint retune from golden seeds; CAR-14 contract) |
| F2.9 | Fixtures versionadas em `data/golden_cases/`; LangSmith opcional |
| F2.10 | Lean prune = must-haves + uma camada de foundation (prereqs) |
| F2.11 | Validation = alinhamento leve de prompts/catálogo aos LLM goals; sem redesign UX/grafo |
| F2.12 | Trabalho interno sem externo começa cedo; harness + aceite golden esperam must-haves frozen |

Linear: [Phase 2 — Goals LLM + prompts + english-first](https://linear.app/career-forge-v2/project/phase-2-goals-llm-prompts-english-first-40c6a783a3b3) · CAR-14…CAR-18

---

### Fase 3 — Rebrand + landing + pilotos (F3a) · platform auth (F3b)

**Split (F3.8):** **F3a** closeable without login; **F3b** = [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) when `borderless-api` issuer exists.

**F3a entrega:** hard-cap P95 bump + rebrand + thin marketing landing (pt-BR chrome) + 2 BASE/PSP humans complete core E2E + short note to Yuri  
**F3b entrega:** Borderless issuer + send resume + account merge (zero code until issuer contract)

**F3a inclui:**

- Kill-switch `COST_P95_BRL_PER_RUN=1.3639`; pool R$500; forge cap/user = 2 (no ops UI)
- Rebrand tokens + logo/favicon + marketing landing composition
- pt-BR marketing + chrome only
- 2 pilots on anon scaffold (login not required)

**Critério de aceite F3a (F3.12):** checklist above + short note to Yuri — **no** formal GO ritual.  
**Pilot E2E (F3.9):** goal → diagnosis → forge SSE → roadmap → ≥1 validation → roadmap reacts (mentor/report out of acceptance).

#### Decisões travadas (grill 2026-08-08)

| # | Decisão |
|---|--------|
| F3.1 | While issuer blocked: ship rebrand + landing + i18n chrome + hard-cap polish; no invite-anon-as-platform-auth workaround |
| F3.2 | Hard caps = config: `COST_P95_BRL_PER_RUN=1.3639`, pool R$500, `FORGE_CAP_PER_USER_MONTH=2`; no ops UI |
| F3.3 | Amend Decision #10: thin marketing on `/career-forge`; product stays at current routes (no `/app` migration) |
| F3.4 | pt-BR = marketing + chrome only; diagnosis/forge/validation AI + prompts stay EN |
| F3.5 | Rebrand = tokens + logo/favicon **and** marketing landing composition; no product redesign |
| F3.6 | Full Borderless login = last eng slice when issuer ready; funnel stays CTA → product; entry gate later |
| F3.7 | 2 pilots do **not** depend on login — E2E valid on anon scaffold |
| F3.8 | Split: F3a closeable without login; F3b = CAR-28 |
| F3.9 | Pilot E2E = goal → diagnosis → forge SSE → roadmap → ≥1 validation → roadmap reacts |
| F3.10 | Pilot who/goals unconstrained |
| F3.11 | Feedback-driven facilitation; no rigid “sem intervenção” gate |
| F3.12 | F3a Done = P95 bump + rebrand + landing/pt-BR chrome + 2 E2E humans + short note to Yuri |

Linear: [Phase 3a — Rebrand + landing + pilots](https://linear.app/career-forge-v2/project/phase-3a-rebrand-landing-pilots-ebc398e30d12) · CAR-33…36 · F3b [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28)

---

## Kick-off / externos

| Item | Status |
|------|--------|
| VPS Labs / Brunno | Deploy OK; **nginx path + domínio** pendente |
| Org `borderlesscodinghub` | Acesso em andamento / parcial OK |
| Budget API | Hard R$500 · gate approval R$700 |
| Landing Frame vs Next | **Next na v2**; thin marketing on `/career-forge` (F3.3); Frame depois |
| Brand kit | **Aprovado** |

---

## Fora de escopo (v3+)

SSO além da platform · NocoDB/Discord · dashboard OPS · certificação/Gate-as-a-Service · monetização Stripe · RAG de vagas no forge · hard block de diagnóstico · Frame landing · domínio global standalone

---

## Estimativa

| Fase | Horas | Prazo |
|------|-------|-------|
| F1 | 15–25h | Semanas 1–2 |
| F2 | 20–30h | Semanas 2–3 |
| F3 | 21–30h | Semanas 4–5 |
| **Total** | **56–85h** | **4–5 semanas** |

---

## Linear backlog — F1

Workspace: [Career Forge V2](https://linear.app/career-forge-v2) · Team key: `CAR`  
Project: [Phase 1 — Infra + cost gate](https://linear.app/career-forge-v2/project/phase-1-infra-cost-gate-7ea0a33e6ef7)

Branch format: `CAR-XX-title-slug` (sem prefixo de username).

### Track A — agora

| Issue | Title |
|-------|-------|
| [CAR-5](https://linear.app/career-forge-v2/issue/CAR-5) | Swap goals + minimal catalog seeds (LLM tracks) |
| [CAR-6](https://linear.app/career-forge-v2/issue/CAR-6) | Cost instrumentation (global pool + per-user cap) |
| [CAR-7](https://linear.app/career-forge-v2/issue/CAR-7) | Synthetic cost gate run + Yuri report (blocked by CAR-5, CAR-6) |
| [CAR-8](https://linear.app/career-forge-v2/issue/CAR-8) | Draft must-have nodes (4 LLM goals) |

### Track B — bloqueada

| Issue | Title |
|-------|-------|
| [CAR-9](https://linear.app/career-forge-v2/issue/CAR-9) | Labs nginx path `/career-forge` (blocked on Brunno) — Backlog |

---

## Linear backlog — F2

Project: [Phase 2 — Goals LLM + prompts + english-first](https://linear.app/career-forge-v2/project/phase-2-goals-llm-prompts-english-first-40c6a783a3b3)

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-14](https://linear.app/career-forge-v2/issue/CAR-14) | CTRR prompt/rubric recalibration + light validation align | [S] | — (internal start OK) |
| [CAR-15](https://linear.app/career-forge-v2/issue/CAR-15) | Soft gate: global bar + lean prune + warnings | [S] | CAR-14 |
| [CAR-16](https://linear.app/career-forge-v2/issue/CAR-16) | English-first hard cutover | [P] | — (∥ CAR-14) |
| [CAR-17](https://linear.app/career-forge-v2/issue/CAR-17) | Must-have forge enforcement + ≥70% harness | [S] | CAR-8 freeze, CAR-15 |
| [CAR-18](https://linear.app/career-forge-v2/issue/CAR-18) | 16 golden cases + rubric + Yuri spot-check | [S] | CAR-14…17 |
