# Career Forge — Handoff F1+F2 → Yuri (prep F3)

> **Data:** 2026-08-05 · **Autor:** Pedro Alano · **Audiência:** Yuri (aprovações) + Pedro (plano)  
> **Notion:** colar este markdown (ou espelhar) como irmão do [Cost gate F1](https://app.notion.com/p/Career-Forge-Gate-de-custo-F1-relat-rio-para-Yuri-Preview-3a704abd19d580709296dc843319e87e)  
> **Repo mirror:** este arquivo · must-haves para Yuri: [docs/product/must-haves/](../product/must-haves/) · goldens: decisão Pedro ([RUBRIC](../product/golden-cases/RUBRIC.md))  
> **Linear:** [CAR-18](https://linear.app/career-forge-v2/issue/CAR-18) (In Progress) · F2 quase fechada

---

## 0. Resumo executivo

| Onde estamos | Detalhe |
|--------------|---------|
| **F1** | Infra Labs + cost instrumentation + gate sintético **GO vs hard stop R$500** (números abaixo). Sign-off Yuri ainda pendente. |
| **Forge recovery** | Epic CAR-22 Done (MVP + Slice 2). Auth anon JWT + artifacts + share/resume. Slice 3 (`borderless-api`) → F3. |
| **F2** | Eng Done (CAR-14…17 + harness CAR-18). Pedro **16/16 PASS** nos goldens (decisão de qualidade fechada por Pedro). Yuri: must-haves + custos. |
| **Bloqueio humano** | Nenhum aluno BASE/PSP até aprovações (custo + must-haves) + auth platform + hard caps (locks V2-PLAN). |

**Pedido a Yuri (3 aprovações separadas):**

| # | Aprovação | Status | O que fazer |
|---|-----------|--------|-------------|
| 1 | **Cost gate F1** (histórico) | ⏳ | Ler [Notion cost gate](https://app.notion.com/p/Career-Forge-Gate-de-custo-F1-relat-rio-para-Yuri-Preview-3a704abd19d580709296dc843319e87e) · confirmar GO vs R$500 |
| 2 | **Must-haves** (4 goals) | ⏳ | Revisar docs + JSON — ver §4.2 (goldens / scorecards = Pedro; sem spot-check de mid) |
| 3 | **Re-cost F2** (stack atual) | ✅ eng GO · ⏳ Yuri | [pt-BR](./2026-08-06-cost-gate.pt-BR.md) · [EN](./2026-08-06-cost-gate.md) — P95 **R$1,36** · proj. **R$90,15** ≪ R$500 |

Com **(1)+(2)** → F2 pode fechar no Linear. Com **(1)+(2)+(3)** → confiança de custo na stack que vai a piloto. Prep F3 (Linear + issuer) já pode correr em paralelo; **piloto humano só depois**.

---

## 1. Ownership (contexto operacional)

F2 foi **executada de ponta a ponta com evidência no repo** (harness, goldens 16/16, re-cost) para chegar a um pacote único de revisão — em vez de pausar a cada gate intermediário. As aprovações do Yuri continuam o **controle de risco** em custo e must-haves: nada de aluno real até isso estar assinado. Qualidade dos goldens / scorecards: **decisão de Pedro** (16/16 PASS).

- Pedro fechou prompts CTRR, soft gate, English-first, must-have forge, harness e scoring 16/16.
- Must-haves: **silence baseline 2026-08-04** — Yuri revisa se os ids ainda batem com sinal de vaga (§4.2).
- Cost gate F1 + re-cost F2: eng GO; aprovação do Yuri ainda aberta.
- Adiantar eng **não** substitui as aprovações de custo/must-haves — concentra a decisão dele nesses artefatos, já medidos.

---

## 2. O que já entregamos (cronológico)

### 2.1 Fase 1 — Infra + cost gate

| Issue | Entrega |
|-------|---------|
| CAR-5 | 4 goals LLM + seeds de catálogo |
| CAR-6 | CostGuard · pool global · cap/user · 429 |
| CAR-7 | Gate sintético + relatório Yuri → **GO** (proj. ~R$72,53 ≪ R$500) |
| CAR-8 | Drafts must-have (4 goals) → silence baseline |
| CAR-9 / 21 / 19 / 20 / 30 | Path Labs `/career-forge`, SSE forge, bake API URL, POST `/forge/runs`, GET `/roadmap/current` |
| CAR-13 | Auto-deploy `main` restaurado |

**Números do gate F1** (artifact `docs/reports/.runtime/cost-gate-75393143-summary.json`, batch ~2026-07-24):

| Métrica | Valor |
|---------|-------|
| Forge n | 24 |
| Forge P95 | **R$1,10** (USD→BRL FX 5,50) |
| Projeção mensal (buffer 1,1) | **R$72,53** |
| Hard stop | R$500/mês |
| Verdict eng | **GO** |

> **Nota importante:** esse batch já usava os **4 goals LLM** (rag / agent / evals / fine-tuning), não fullstack legado. O que ficou desatualizado vs hoje é a **estrutura de runtime F2** (soft gate lean, bias+inject must-haves, prompts EN recalibrados) — daí o ack **#3**.

### 2.2 Forge recovery + auth scaffold (∥ F2) — epic Done

| Issue | Entrega |
|-------|---------|
| CAR-23 | `AuthProvider` + Bearer JWT anon |
| CAR-24 / 25 | `forge_artifacts` + list/open freeze-before-promote |
| CAR-26 | Stream ticket (Bearer → `?ticket=`) |
| CAR-27 | Share + resume + Continue na landing |
| CAR-29 / 31 | Slice 2 `/forges` rico + polish UX |
| CAR-28 | **Backlog / F3** — issuer `borderless-api` (sem acesso ainda; zero prep de código) |

ADR: [ADR-003](../decisions/ADR-003-forge-recovery-auth-scaffold.md).

### 2.3 Fase 2 — Goals LLM + prompts + english-first

| Issue | Entrega | Status |
|-------|---------|--------|
| CAR-14 | CTRR EN + 5 dims + `profile_score` + validation leve | Done |
| CAR-15 | Soft gate global + lean prune + warnings | Done |
| CAR-16 | English-first hard cutover | Done |
| CAR-32 | Docs ADR/V2-PLAN ↔ 5 dims | Done |
| CAR-17 | Must-have bias+inject + harness ≥70% | Done |
| CAR-18 | 16 goldens + rubric; must-haves para Yuri | Harness + Pedro **16/16 PASS** (goldens fechados) · must-haves **Yuri ⏳** |

Docs: [PEDRO-RUNBOOK](../product/golden-cases/PEDRO-RUNBOOK.md) · [RUBRIC](../product/golden-cases/RUBRIC.md) · cutoff [0.50](../product/golden-cases/SOFT-GATE-CUTOFF.md).

---

## 3. Decisões locked (relevantes agora)

### Aceitação F2 / QA

| # | Decisão |
|---|--------|
| F2.1 | 16 casos = 4 goals × 4 personas (early / mid / staff / soft-gated-weak) |
| F2.2 | Pedro scoreia e **fecha** os 16 goldens; Yuri revisa só as **listas must-have** (não os mid scorecards) |
| F2.3 | Soft-gate cutoff global **0,50** (midpoint weak 0,42 / early 0,58) |
| F2.4 | ≥70% must-have **pre-inject** nos 12 non-weak; weak prova lean/gate |
| F2.5 | Must-haves: silence baseline 2026-08-04 até Yuri pedir edit |
| F2.6 | English-first no produto; pt-BR na F3 |
| F2.7 | F2 100% sintético/interno — sem aluno real |
| F2.8 | Ownership: eng F2 + goldens fechados por Pedro; Yuri = custo + must-haves antes de humano |

### Restrições F3 (não reabrir sem grill)

| # | Decisão |
|---|--------|
| 1 | Auth issuer via `borderless-api` no 1º humano |
| 2 | Hard stop R$500 + cap/user; kill-switch por P95 |
| 3 | Soft gate no piloto (não hard block de diagnóstico) |
| 4 | Primeiro humano só após gate + golden + auth platform + caps |
| 5 | Landing path `/career-forge` + app; rebrand Borderless |
| 6 | CAR-28: zero implementação até contrato do issuer existir |

Fonte canônica: [V2-PLAN.md](../V2-PLAN.md) decision log + § Fase 2.

---

## 4. Verificações do Yuri (#1 e #2)

### 4.1 Cost gate F1 (#1)

- Abrir: [Notion — Gate de custo F1](https://app.notion.com/p/Career-Forge-Gate-de-custo-F1-relat-rio-para-Yuri-Preview-3a704abd19d580709296dc843319e87e)
- Confirmar: proj. ~R$72 ≪ R$500 → **GO** (ou CONDITIONAL/NO-GO com motivo)
- Responder neste Notion / Linear CAR-7 ou CAR-18 com data + aprovação

### 4.2 Must-haves (#2)

**Fora de escopo do Yuri:** fixtures mid / scorecards A–E / harness golden — Pedro já aceitou **16/16 PASS** ([RUBRIC.md](../product/golden-cases/RUBRIC.md) appendix).

**Pedir revisão:** as 4 listas must-have (sinal de vaga ainda faz sentido?).

| Goal | Doc | JSON |
|------|-----|------|
| rag-engineer | [must-haves/rag-engineer.md](../product/must-haves/rag-engineer.md) | `data/must-haves/rag-engineer.json` |
| agent-engineer | [must-haves/agent-engineer.md](../product/must-haves/agent-engineer.md) | `data/must-haves/agent-engineer.json` |
| llm-evals | [must-haves/llm-evals.md](../product/must-haves/llm-evals.md) | `data/must-haves/llm-evals.json` |
| fine-tuning | [must-haves/fine-tuning.md](../product/must-haves/fine-tuning.md) | `data/must-haves/fine-tuning.json` |

Baseline: silence 2026-08-04. Resposta: OK ou edits pedidos (Notion / Linear CAR-18).

**Não obrigatório:** passe UI Labs.

---

## 5. Re-cost F2 (ack #3) — resultado 2026-08-06

### 5.1 Evidência

| Fonte | Resultado |
|-------|-----------|
| Golden LIVE (2026-08-05) | 16 forges OpenAI — **custo não persistido** (`InMemoryUsageStore` + `billable=False`) |
| Gate F1 (2026-07-24) | Baseline pré soft-gate/inject — P95 **R$1,10** · proj. **R$72,53** |
| **F2 re-cost (2026-08-06)** | batch `cd786c94` · path `apply_lean_forge_input` + personas mid/early/staff/weak · **32/32 OK** |

Relatório: [pt-BR](./2026-08-06-cost-gate.pt-BR.md) · [EN](./2026-08-06-cost-gate.md) · ledger `docs/reports/.runtime/cost-gate-cd786c94.*`

### 5.2 Comparativo F1 → F2

| Métrica | F1 (histórico) | **F2 (novo)** |
|---------|----------------|---------------|
| Forge n | 24 | 24 (+ 4 soft-gated lean) |
| Forge mean BRL | 0,73 | **0,96** |
| Forge P95 BRL | **1,10** | **1,36** |
| Projeção buffered BRL | 72,53 | **90,15** |
| vs hard R$500 | GO | **GO** |

P95 subiu ~24% (prompts/must-have bias / grafos mais ricos). Continua **muito abaixo** do hard stop.

### 5.3 Env recomendado (após aprovação do Yuri)

```bash
COST_P95_BRL_PER_RUN=1.3639
COST_BUFFER_FACTOR=1.10
COST_FX_USD_BRL=5.50
```

### 5.4 Pedido Yuri (ack #3)

Confirmar **GO** no re-cost F2 (ou CONDITIONAL/NO-GO). Não precisa reabrir o hard stop R$500 — só validar que a stack atual ainda cabe.

---

## 6. Próximos passos (Pedro) — prep F3

Ordem (grill 2026-08-05):

1. **Aprovações do Yuri** (#1 cost F1 · #2 must-haves · #3 re-cost F2) — eng do #3 já entregue  
2. **Grill + issues Linear F3** (auth platform, caps hard, rebrand, landing, 2 pilotos)  
3. **Destravar acesso `borderless-api`** (desbloqueia CAR-28)  
4. Só então: implementação rebrand / landing / caps duros / pilotos E2E  
5. Após #3: bump `COST_P95_BRL_PER_RUN` → **1.3639** (kill-switch)  

**Permitido agora:** planejamento, Linear, chase de issuer.  
**Proibido até aprovações de custo/must-haves + auth + caps:** aluno real no funil.

F3 no plano ([V2-PLAN](../V2-PLAN.md) § Fase 3):

- Auth mínima via `borderless-api`
- Caps hard (pool R$500 + per-user)
- Rebrand Borderless + i18n pt-BR
- Landing Next.js `/career-forge`
- 2 pilotos BASE/PSP end-to-end

---

## 7. Como registrar as aprovações

Resposta preferida (Notion ou Linear CAR-18):

```text
#1 Cost F1: GO | CONDITIONAL | NO-GO — <data> — <nota>
#2 Must-haves: OK | edits requested — <data> — <nota>
#3 Re-cost F2: GO | CONDITIONAL | NO-GO — <data>
```

Pedro atualiza STATUS / must-have docs quando as aprovações entrarem.

---

## Links rápidos

| Recurso | Link |
|---------|------|
| Cost gate Notion F1 | https://app.notion.com/p/Career-Forge-Gate-de-custo-F1-relat-rio-para-Yuri-Preview-3a704abd19d580709296dc843319e87e |
| CAR-18 | https://linear.app/career-forge-v2/issue/CAR-18 |
| Must-haves | [docs/product/must-haves/](../product/must-haves/) |
| Goldens (Pedro) | [RUBRIC.md](../product/golden-cases/RUBRIC.md) · `data/golden_cases/` |
| STATUS | [STATUS.md](../STATUS.md) |
| ROADMAP | [ROADMAP.md](../ROADMAP.md) |
| V2-PLAN | [V2-PLAN.md](../V2-PLAN.md) |
| Labs | https://labs.borderlesscoding.com/career-forge |
