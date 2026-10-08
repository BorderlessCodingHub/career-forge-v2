# Career Forge v3 — Plano de execução

> Borderless · labs.borderlesscoding.com/career-forge  
> **Atualizado:** 2026-10-07  
> **Mapa:** [Career Forge V3](https://linear.app/career-forge-v2/issue/CAR-109)  
> Cada decisão mora no ticket. Este arquivo é o corte para construir.

V3 devolve o learner a um Roadmap que já existe, cobra o `external` a **USD $7/mo**, e pendura um Video Reference em cada Node. Não abre mercado, não cria V3b, e não constrói o que está na névoa.

**Público:** BASE e PSP incluídos. `external` paga. Welcome não hospeda checkout.

---

## V3a — uma fase, quatro trilhos paralelos

Nenhum trilho bloqueia o início dos outros. Classe **[P]** entre trilhos. A única sequência **[S]** é a virada live do Stripe, e ela não segura os demais.

Epic: [V3a](https://linear.app/career-forge-v2/issue/CAR-122).

| Trilho | Classe | Issue |
|--------|--------|-------|
| Continuity email | **[P]** | [V3a: Continuity email](https://linear.app/career-forge-v2/issue/CAR-123) |
| Video References | **[P]** | [V3a: Video References](https://linear.app/career-forge-v2/issue/CAR-124) |
| Stripe copy | **[P]** | [V3a: Welcome and paywall say USD $7/mo](https://linear.app/career-forge-v2/issue/CAR-125) — pode ir a `main` antes do Portal |
| Portal + Billing email | **[P]** | [V3a: Customer Portal and Billing email](https://linear.app/career-forge-v2/issue/CAR-126) |
| Sentry DSN no deploy | **[P]** | [V3a: Pass the Sentry frontend DSN in the Labs deploy](https://linear.app/career-forge-v2/issue/CAR-127) |
| Chaves live | **[S]** | [Provision Stripe Price and keys for Labs](https://linear.app/career-forge-v2/issue/CAR-121) e um Checkout sandbox. Não bloqueia os trilhos acima. |

Não há **[B]** para começar a V3a.

---

## Continuity email

[Inactivity Continuity email contract](https://linear.app/career-forge-v2/issue/CAR-110) · [Next-Node Continuity email contract](https://linear.app/career-forge-v2/issue/CAR-111)

Um **quiet stretch** são 168 horas UTC desde a última **Roadmap presence** (abrir o Roadmap, marcar checklist, validar, forjar, abrir um Reference). Refresh de token, Welcome, abrir o email e um clique que para no Identity gate não contam.

Um envio aceito por quiet stretch. Envio rejeitado pelo mailer não gasta o stretch. Presença nova recomeça as 168 horas. Sem opt-out.

Na hora do envio:

- Existe **next Node** (primeiro Node da spine que não está aprovado nem locked) → o email nomeia esse Node e o link abre nele.
- Não existe → o email de inatividade ainda sai, e o link abre o Roadmap.

Sem Email identity, o link passa pelo Identity gate e segue. Se o Node já não for o next Node na chegada, abre o Roadmap. A copy não diz que o learner está atrasado. O texto exato é do build.

O Billing email não gasta nem pausa o quiet stretch.

---

## Video References

[Video search API options for forge References](https://linear.app/career-forge-v2/issue/CAR-114) · [Where video search sits in the Forge](https://linear.app/career-forge-v2/issue/CAR-115) · [Video Reference quality bar](https://linear.app/career-forge-v2/issue/CAR-116)

Uma passagem YouTube Data API depois de `graph_ready`, fora da timeline. Os vídeos entram nos Nodes mesmo se o Roadmap já estiver aberto. Falha da busca deixa os Nodes só com docs e não tenta de novo.

Um vídeo por Node: 4–20 min, inglês, embeddable, qualquer canal, sem piso de views. Docs oficiais continuam preferidos quando empatam. Anexar antes da allowlist do YouTube. Até o embed funcionar, o **Escape hatch** abre o host. O `no-referrer` de `/reference` quebra o embed do YouTube até esse conserto, que é parte deste trilho.

---

## Stripe

[Stripe Portal and dunning events for current adapter](https://linear.app/career-forge-v2/issue/CAR-113) · [Continuity vs billing email ownership](https://linear.app/career-forge-v2/issue/CAR-119) · [$15 Stripe Price vs Welcome copy lock](https://linear.app/career-forge-v2/issue/CAR-120) · [ADR-005](./decisions/ADR-005-identity-gate-product-entry.md)

### Preço e copy — [P]

Um Price: **USD $7, mensal**. Sem Price em BRL, sem anual, sem trial. Welcome, o paywall e o glossário dizem USD $7/mo. Checkout pode mostrar esse valor em BRL (Adaptive Pricing). Welcome e o paywall ficam em USD. Welcome não hospeda checkout.

O paywall deixa de dizer “Free forge used” e “subscribe to continue”. Ele nomeia USD $7/mo e diz que assinar é o que inicia diagnosis e forge. BASE e PSP não veem o painel. O texto exato é do build.

Labs usa chaves e Price de teste, no mesmo USD $7/mo, até um Checkout sandbox completar. Aí sim chaves live e o Price live (**[S]**).

### Portal + Billing email — [P]

`past_due` continua entitled. O Portal é `POST /v1/billing_portal/sessions` mais `POST /billing/portal`. Sem ação de Stripe no Operator console.

**Billing email** é outro trilho, não Continuity. Vai para um `external` pagante cujo charge falhou enquanto a Entitlement ainda vale. Um envio aceito por **failed-charge spell** (do charge falho até um charge posterior que sucede). Retry dentro do spell não reenvia. Career Forge envia. O email de failed-payment do Stripe Dashboard fica desligado.

A copy diz que o charge falhou, que dá para continuar usando o Career Forge, e que o link atualiza o cartão. Não nomeia o next Node, não diz que a pessoa está atrasada, e não diz que o acesso acabou.

O link é uma URL do Career Forge. Sem Email identity, passa pelo Identity gate e abre uma sessão nova do Portal na atualização do payment method. Esse clique não é Roadmap presence. Ao sair do Portal, volta ao Roadmap que o produto já abre; sem Roadmap, volta à entrada do produto. Cair no Roadmap começa um quiet stretch novo.

Sem opt-out, e sem um switch que também cale a Continuity email. Nenhum outro email de billing: nada quando a Entitlement acaba, nada quando o primeiro checkout nunca sucede, nada quando o charge tira a Entitlement no mesmo instante.

---

## Sentry — [P]

[Sentry topology for Labs Career Forge](https://linear.app/career-forge-v2/issue/CAR-112) · [Provision Sentry for Career Forge](https://linear.app/career-forge-v2/issue/CAR-118) (Done, PR #88)

Dois projetos (frontend e backend). DSN no env de Labs. `environment=labs`. Release = git SHA. Email e PII fora do evento. Público é engenheiro. Sem UI de learner e sem faixa de erro no Operator.

O que a V3a ainda faz: o workflow de deploy passa `NEXT_PUBLIC_SENTRY_DSN` como build arg do Next.js. O backend já lê `SENTRY_DSN` na subida do container.

---

## Fora da V3a

Ficam sem fase até uma decisão futura, não como V3b:

- Cobertura canônica de `/learn` além dos cinco corpos de RAG
- Cadência de mastery (quando validar / mock)
- Continuidade dentro do produto (bell, banner)
- Faixa de erros recentes no Operator

Fora deste plano: Discord, NocoDB, Job-RAG, domínio standalone, certificação, diagnosis hard-block, streaks, badges, checkout na Welcome, pt-BR, Stripe no Operator console, SSO além da Borderless.

---

## Aberto

[Provision Stripe Price and keys for Labs](https://linear.app/career-forge-v2/issue/CAR-121) — tarefa, não decisão. Price USD $7/mo de teste e depois live, sem trial, sem Price em BRL, Adaptive Pricing no Checkout. Segredos fora do git. É a porta das chaves live. Não segura os outros trilhos da V3a.
