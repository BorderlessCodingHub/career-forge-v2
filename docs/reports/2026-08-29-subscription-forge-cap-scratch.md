# Scratch: $10 vs $15/mês × cap de forges

Simulação de COGS (custo de API por assinante) e lucro bruto. Não altera preço público, Stripe nem o cap atual de 2 forges.

Câmbio: **1 USD = R$5,50**. Stripe: **2,9% + $0,30**. Buffer no P95: **110%**. Pool global: **R$500/mês**. Piloto: **30** pagantes.

Lucro bruto ≈ receita − Stripe − COGS.

---

## Mix mensal por assinante (cap 2)

Custo unitário da avaliação de node (mock + gap):

| Item | USD / run |
|------|----------:|
| Mock interview | **$0,0049** (média de 2 runs: $0,0047 e $0,0051) |
| Gap classifier | **$0,00078** |
| **Sessão de 1 node** (2 mock + 1 gap) | **~$0,011** |

| Item | n / mês | USD |
|------|--------:|----:|
| Forge | 2 | 2 × $0,175 = **$0,35** (média) · P95+buffer ~**$0,55** |
| Diagnosis (sessão 4 turnos) | 1 | **$0,0009** |
| Tutor | 10 msgs | **$0,0083** |
| Avaliação de node (mock + gap) | 4 | 4 × $0,011 = **$0,044** |
| Validação rubric (sem LLM) | 4 | **$0** |
| **Total esperado** | | **~$0,40** |

20 mensagens de tutor: +$0,017. Loops de diagnosis / tutor / mock / gap continuam irrelevantes vs $10 / $15 e **não mudam** a matriz de forges abaixo.

---

## Matriz $10 vs $15 × cap de forges

| Forges/mês | COGS médio | COGS P95+buf | Lucro **$10** (P95) | Lucro **$15** (P95) | Max pagantes no pool | Pool @ 30 users |
|-----------:|-----------:|-------------:|--------------------:|--------------------:|-------------------:|----------------:|
| **2 (hoje)** | $0,35 | $0,55 | **$8,86** | **$13,72** | 166 | R$90 |
| 3 | $0,53 | $0,82 | $8,59 | $13,45 | 110 | R$135 |
| 4 | $0,70 | $1,09 | $8,32 | $13,17 | 83 | R$180 |
| 5 | $0,88 | $1,37 | $8,05 | $12,90 | 66 | R$225 |
| 6 | $1,05 | $1,64 | $7,77 | $12,63 | 55 | R$270 |
| 8 | $1,40 | $2,18 | $7,23 | $12,08 | 41 | R$360 |
| 10 | $1,76 | $2,73 | $6,68 | $11,54 | 33 | R$450 |
| 12 | — | ~$3,27 | — | — | ~27 | **R$540 OVER** |

Cada forge extra: ~$0,18 (média) / ~$0,27 (P95). $15 vs $10 vale ~**+$5/user** em qualquer cap.

### Piloto de 30 pagantes

| Forges | Lucro @ $10 | Lucro @ $15 |
|-------:|------------:|------------:|
| 2 | ~$272 | **~$417** |
| 6 | ~$251 | ~$396 |
| 10 | ~$230 | ~$375 |

A 10 forges o piloto ainda cabe (R$450 < R$500). A **12** estoura.

### Pool saturado (teto R$500)

Mais forges = menos seats. O COGS do pool continua ~$91; cai a receita.

| Forges | Max users | Lucro no teto @ $10 | Lucro no teto @ $15 |
|-------:|----------:|--------------------:|--------------------:|
| 2 | 166 | ~$1 471 | **~$2 277** |
| 4 | 83 | ~$690 | ~$1 093 |
| 6 | 55 | ~$427 | ~$695 |
| 10 | 33 | ~$220 | ~$381 |

### Leitura

- **$10 · 2–3 forges** — perto do cap atual
- **$15 · 4–6 forges** — piloto de 30 ainda cabe; margem ~$13/user
- **10 forges** — só com cohort pequeno (~33 pagantes no teto)

BASE/PSP included comem forges a receita $0 e entram no mesmo R$500.
