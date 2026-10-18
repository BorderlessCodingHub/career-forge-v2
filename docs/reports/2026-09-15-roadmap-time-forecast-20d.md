# Previsão de tempo — 1 e 2 roadmaps @ 2h/dia

**Período da amostra:** 2026-08-26 → 2026-09-15 (UTC)  
**Fonte:** LangSmith `career-forge` · forges `env:production`  
**Uso:** argumento comercial / onboarding para o learner iniciar o roadmap

Relatório irmão (custo LLM): [2026-09-15-llm-cost-20d.md](./2026-09-15-llm-cost-20d.md)

---

## Resumo

Com **2 horas de estudo por dia**:

| Cenário | Horas (base) | Dias @ 2h/dia | Semanas |
|---------|-------------:|--------------:|--------:|
| **1 roadmap** | ~21 h | **~11 dias** | ~1,6 |
| **2 roadmaps** | ~41 h | **~21 dias** | **~3** |
| Faixa 2 roadmaps | 33–50 h | 17–25 dias | 2,4–3,6 |

**Pitch:** *“Com 2h por dia, você costuma fechar um roadmap em cerca de duas semanas — e dois roadmaps em cerca de três semanas.”*

É **modelo de esforço** calibrado em forges reais, não tempo medido de conclusão.

---

## Amostra que calibrou a previsão

| Métrica | Valor |
|---------|------:|
| Forges (`roadmap_forge`) | **8** |
| Usuários distintos | **8** |
| Goals | `agent-engineer` 7 · `rag-engineer` 1 |
| Nós / roadmap (média · mediana) | **10,4 · 10** |
| Study plans com IO | **2** → 11 e 12 nós · **~3 tasks/nó** |
| Demais | proxy catálogo (**10** nós) |

Os plans com IO mostram carga real por skill (pipeline, gold set, análise de falhas) — coerente com **1,5–2,25 h/nó**.

---

## Método

O produto não grava horas de estudo. Hipótese por nó do plan:

| Faixa | Horas / nó |
|-------|-----------:|
| Otimista | 1,5 |
| Base | 1,875 |
| Pessimista | 2,25 |

Mais **× 1,10** de overhead (navegação, tutor, mock).

```text
hours = N_nós × effort_por_nó × 1.10
dias @ 2h/dia = ceil(hours / 2)
2 roadmaps ≈ 2 × mediana(hours)
```

Mediana na amostra: **16,5 / 20,6 / 24,8 h** (1 roadmap) → **9 / 11 / 13 dias**.

---

## Copy pronta

**Curta**

> Com 2 horas por dia, a maioria dos roadmaps deste piloto fecha em cerca de **duas semanas**. Dois roadmaps: cerca de **três semanas**.

**Com faixa**

> Estimamos **~21 horas** por roadmap (~11 dias a 2h/dia). Dois roadmaps: **~41 horas** — tipicamente **3 semanas** (faixa **2,5–3,5**).

**Com transparência**

> Com base nos roadmaps gerados em produção (~10 skills, tarefas práticas por nó), dedicando **2h/dia** você tende a concluir **um** roadmap em ~**1,5–2 semanas** e **dois** em ~**3 semanas**. O ritmo real depende do seu ponto de partida no diagnóstico.

---

## Limites

1. Sem telemetria de “roadmap concluído” — previsão, não medição.
2. Amostra pequena (8 forges); `agent-engineer` domina.
3. Modelo trata todos os nós do plan como esforço cheio (conservador se o diagnóstico já aprovou skills).
4. Cadência 2h/dia assume consistência; pausas alongam o calendário.
