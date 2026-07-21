# Career Forge v2 — Plano de Execução

> Borderless · labs.borderlesscoding.com/career-forge  
> Executor: Pedro Alano  
> Prazo estimado: 4–5 semanas ·  
> **Atualizado:** 2026-07-20 — grill + respostas Yuri (auth platform, budget, público BASE/PSP)

---

## Visão

Career Forge v2 reposiciona o motor AI-native de aprendizado para **LLM engineers**: 4 goals especializados, prompts calibrados para o espectro BASE/PSP (6 meses → 40 anos de XP), english-first, e rebrand Borderless. O motor LangGraph (diagnóstico CTRR → forge → validação) permanece intocado.

**Não é redesign.** É reposicionamento de goals, prompts, catálogo e identidade visual.

**Público:** somente alunos BASE e PSP.

---

## Decision log (travado)

| # | Decisão |
|---|--------|
| 1 | Auth via `borderless-api` (platform) — **não** na F1; entra na **F3** com o 1º humano. Magic link local do plano antigo: fora. |
| 2 | Hard stop API: **R$500/mês** (pool global). **R$700** = teto de *aprovação* do gate F1 (não o kill-switch). |
| 3 | Throttle: **pool global R$500** + **cap por usuário** (1–2 forges/mês; número fino pós-gate). |
| 4 | Funil único (4 goals); barra de passagem por **evidência CTRR**, não por anos de XP. |
| 5 | “Não passa” no diagnóstico = **soft gate** no piloto (forge lean + aviso). Hard block = v2.1 após calibrar nota. |
| 6 | Output bom = LEAN com fit ≥70% dos **must-have nodes** derivados de corpus de vagas. **QA humano**, não RAG de jobs no produto v2. |
| 7 | Kill-switch runtime = **GraphRuns × P95 BRL** medido no gate F1 (+ buffer ~10%). LangSmith audita. |
| 8 | Pool conta **toda GraphRun billable** (diagnosis, forge, validation, mentor). Demo-ana + sintéticos do gate: fora do pool de aluno, dentro do relatório F1. |
| 9 | Primeiro humano BASE/PSP: **somente na F3** (após gate + golden cases + auth platform + caps). F2 100% interno/sintético. |
| 10 | URL: **path** — `labs.borderlesscoding.com/career-forge` (landing) + `/career-forge/app` (produto). Frame depois, mesmo path. |
| 11 | Must-haves: draft Pedro (1 pág/goal) → 1 rodada sign-off Yuri; silêncio = baseline. |
| 12 | F1 em Track A (desbloqueado) / Track B (nginx path — aguarda Brunno/domínio). Restante de org/deploy Track B já OK. |

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
- Cap por usuário (env: `FORGE_CAP_PER_USER_MONTH`, default pós-gate 1–2)
- Contadores no banco por usuário + agregado mensal de GraphRuns billable
- Monitoramento contínuo via LangSmith

### Autenticação

- **F1/F2:** sem auth de aluno — só sintéticos / uso interno. Caps instrumentados, não expostos a BASE/PSP
- **F3:** integração mínima com `borderless-api` (platform) — validar token → `user_id` estável; desbloqueia cap hard e piloto
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

Dimensões mantidas (Conceptual / Technical / Readiness / Resourcefulness).  
Prompts/rubrics: de “iniciante em transição” → espectro real (early ↔ staff), com perguntas práticas de aplicação e system AI design.

Soft gate: abaixo da nota mínima → aviso + forge lean (não bloqueia no piloto).

16 golden cases (4 goals × 4 dimensões) = critério de QA da F2.

### English-first

- UI, prompts, catálogo e relatórios em inglês desde a F2
- pt-BR como locale secundária (F3)
- Público PSP/BASE compatível

### Landing page

- **v2:** Next.js no path Labs (`/career-forge` marketing, `/career-forge/app` produto)
- Frame: só quando houver comercialização/growth para fora (fora do horizonte atual)
- Demo do forge streaming reutiliza componentes existentes

### Rebrand

- Identidade: #121212 / #5316CC / #44D5AD + brand kit Borderless (aprovado)
- Escopo: tokens Tailwind, logo SVG, favicon — sem redesign estrutural
- Entrega: F3

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
**Sem alunos reais.**

---

### Fase 3 — Rebrand + auth platform + landing + pilotos

**Entrega:** 2 alunos BASE/PSP completam 1 trilha end-to-end sem intervenção + landing no ar  
**Inclui:**

- Auth mínima via `borderless-api` (platform)
- Caps hard ligados (pool R$500 + per-user)
- Rebrand Borderless + i18n pt-BR
- Landing Next.js em `/career-forge`

**Critério de aceite:** sign-off Yuri  

---

## Kick-off / externos

| Item | Status |
|------|--------|
| VPS Labs / Brunno | Deploy OK; **nginx path + domínio** pendente |
| Org `borderlesscodinghub` | Acesso em andamento / parcial OK |
| Budget API | Hard R$500 · gate approval R$700 |
| Landing Frame vs Next | **Next na v2**; Frame depois |
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
