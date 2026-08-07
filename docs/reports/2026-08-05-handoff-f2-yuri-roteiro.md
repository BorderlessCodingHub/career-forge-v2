# Roteiro — Handoff F1+F2 → Yuri (gravação + relatório)

> **Fonte:** [2026-08-05-handoff-f2-yuri.md](./2026-08-05-handoff-f2-yuri.md)  
> **Duração alvo:** 6–8 min · **Idioma:** pt-BR  
> **Uso:** teleprompter / gravação Loom · bloco final cola no Notion

---

## Dicas de tela

| Momento | Abrir na tela |
|---------|----------------|
| Pedidos | Tabela das 3 aprovações (handoff §0) |
| Custo | Comparativo F1→F2 (handoff §5.2) |
| Must-haves | Lista dos 4 goals (handoff §4.2) |
| Fechamento | Template de resposta (handoff §7) |

---

## Roteiro de gravação

### 0. Abertura (~30s)

Yuri, este é o handoff F1+F2 do Career Forge.

Objetivo: três aprovações suas. Engenharia e qualidade dos goldens já estão fechadas por mim. Sem aluno real até custo, must-haves e auth de plataforma.

---

### 1. Onde estamos (~1 min)

F1: infra Labs, CostGuard e gate sintético — projeção histórica cerca de R$72 contra hard stop de R$500.

Forge recovery, epic CAR-22: Done — JWT anônimo, artifacts, share e resume. O issuer Borderless fica pra F3.

F2: engenharia Done. Goldens **dezesseis de dezesseis PASS** — decisão de qualidade minha. Falta você nos must-haves e nos custos.

---

### 2. O que peço (~1 min)

Três aprovações separadas:

**Número um** — Cost gate F1: Notion histórico, confirmar GO versus R$500.

**Número dois** — Must-haves dos quatro goals: listas de skills, não os scorecards mid.

**Número três** — Re-cost F2, stack atual: P95 **R$1,36**, projeção **R$90** — ainda bem abaixo de R$500. Eng já deu GO; falta o seu ack.

Com um e dois, F2 fecha no Linear. Com as três, temos confiança de custo pro piloto. Prep F3 pode correr em paralelo; piloto humano só depois.

---

### 3. Ownership (~30s)

Adiantei eng pra concentrar a decisão em artefatos medidos. Isso não substitui as suas aprovações.

Goldens = Pedro. Custo e must-haves = Yuri.

---

### 4. Entregas em três blocos (~2 min)

**F1:** quatro goals LLM, CostGuard, gate sintético, path Labs, auto-deploy.

**Forge recovery:** auth scaffold anônimo Done; CAR-28, borderless-api, fica backlog F3.

**F2:** CTRR em inglês, soft gate 0,50, English-first, must-have inject, harness com dezesseis goldens — tudo PASS.

---

### 5. Números de custo (~1 min)

F1: P95 R$1,10 · projeção R$72.

F2: P95 R$1,36 · projeção R$90 — subiu cerca de 24% por prompts e must-haves, mas GO claro versus R$500.

Depois do seu GO no número três, bumpamos o kill-switch pra `COST_P95_BRL_PER_RUN=1.3639`.

---

### 6. O que você revisa (~1 min)

**Número um:** Notion do cost gate F1 → GO, CONDITIONAL ou NO-GO.

**Número dois:** quatro docs must-have — rag-engineer, agent-engineer, llm-evals, fine-tuning. Os ids ainda batem com sinal de vaga? OK ou edits.

**Número três:** relatório re-cost F2 → GO.

Não precisa spot-check de mid nem passe UI Labs.

---

### 7. Próximos passos + fechamento (~1 min)

Depois das aprovações: grill F3, destravar borderless-api, só então rebrand, caps duros e dois pilotos.

Agora: planejamento e chase de issuer. Proibido: aluno no funil.

Resposta preferida no Notion ou no CAR-18:

`#1 GO · #2 OK · #3 GO` — com data.

Obrigado.

---

## Relatório curto (colar no Notion / e-mail)

```text
Assunto: Career Forge — Handoff F1+F2 · 3 aprovações

Resumo
- F1 + Forge recovery + F2 eng: entregues.
- Goldens: 16/16 PASS (Pedro).
- Bloqueio: custo (#1+#3) + must-haves (#2) + auth platform antes de humano.

Pedidos
1. Cost F1 — Notion → GO vs R$500 (proj. ~R$72)
2. Must-haves — 4 goals → OK ou edits (sem mid scorecards)
3. Re-cost F2 — P95 R$1,36 · proj. R$90 ≪ R$500 → GO

Resposta
#1 Cost F1: GO | CONDITIONAL | NO-GO — <data>
#2 Must-haves: OK | edits — <data>
#3 Re-cost F2: GO | CONDITIONAL | NO-GO — <data>

Links
- Handoff: docs/reports/2026-08-05-handoff-f2-yuri.md
- Cost F1 Notion: https://app.notion.com/p/Career-Forge-Gate-de-custo-F1-relat-rio-para-Yuri-Preview-3a704abd19d580709296dc843319e87e
- Re-cost F2: docs/reports/2026-08-06-cost-gate.pt-BR.md
- Must-haves: docs/product/must-haves/
- CAR-18: https://linear.app/career-forge-v2/issue/CAR-18
- Labs: https://labs.borderlesscoding.com/career-forge
```

---

## Checklist pré-gravação

- [ ] Handoff aberto na §0 (tabela de aprovações)
- [ ] Re-cost pt-BR aberto na §5.2 (comparativo)
- [ ] Pasta must-haves aberta (4 goals)
- [ ] Notion cost F1 em aba separada
- [ ] Microfone / Loom pronto
