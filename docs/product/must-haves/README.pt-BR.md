# Nós must-have — rascunho F1 (CAR-8)

> Versão em inglês (fonte canônica): [README.md](./README.md)

A aceitação do lean forge na F2 mede **≥70% de cobertura pós-forge** desses must-haves (por goal), via QA humano — não RAG de vagas no produto ([V2-PLAN.md](../../V2-PLAN.md)).

| Goal | Doc | Nós | Tamanho do corpus |
|------|-----|-----|-------------------|
| `rag-engineer` | [rag-engineer.pt-BR.md](./rag-engineer.pt-BR.md) | 10 | 32 |
| `agent-engineer` | [agent-engineer.pt-BR.md](./agent-engineer.pt-BR.md) | 10 | 30 |
| `llm-evals` | [llm-evals.pt-BR.md](./llm-evals.pt-BR.md) | 10 | 28 |
| `fine-tuning` | [fine-tuning.pt-BR.md](./fine-tuning.pt-BR.md) | 10 | 28 |

## Protocolo de sign-off

1. **Rascunho** (CAR-8) — Pedro redige a partir de um corpus enxuto de vagas (~25–40 fontes/goal).
2. **Uma rodada** — Yuri revisa; silêncio = **congelamento do baseline** para o harness da F2 (CAR-17 / CAR-18).
3. **Wiring** — prune + bias/inject + harness de cobertura em **CAR-17**. Aceite formal golden = **CAR-18**.

## Freeze (CAR-17)

**Silence baseline — congelado 2026-08-04 por Pedro.** Spot-check do Yuri → CAR-18. SoT máquina: `data/must-haves/*.json`.


## Notas de amostragem

- Amostrado em **2026-07** a partir de boards públicos de ATS (Lever, Greenhouse, Ashby, páginas de carreira) mais guias de contratação que sintetizam requisitos de vagas.
- Freq = fração aproximada das fontes do corpus que mencionam a skill (ou um sinônimo claro). Não é um estudo estatístico de mercado.
- Títulos em inglês primeiro; fit enxuto para BASE/PSP (sinais de mercado de trabalho, não pesquisa exaustiva de IR).
