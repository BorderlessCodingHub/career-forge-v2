# Career Forge v3 — Plano de execução

> Borderless · labs.borderlesscoding.com/career-forge  
> **Atualizado:** 2026-10-08  
> **Mapa:** [Career Forge V3](https://linear.app/career-forge-v2/issue/CAR-109)  
> Cada decisão mora no ticket. Este arquivo é o corte para construir.

V3 devolve o learner a um Roadmap que já existe, deixa o `external` forjar uma vez e depois cobra **USD $7/mo**, pendura um Video Reference em cada Node, e abre a interface do learner em pt-BR além do inglês. Não abre mercado, não cria V3b, e não constrói o que está na névoa.

**Público:** BASE e PSP incluídos, com 2 forges concluídos por mês UTC. `external` — membership FREE, ou sem conta na Borderless — tem um forge na vida da conta e depois a assinatura. Welcome não hospeda checkout.

---

## V3a — uma fase

Trilhos **[P]** começam juntos. Sequências **[S]**: o gate freemium depois da leitura do perfil, a copy do paywall depois desse gate, e os emails e o roadmap no idioma depois da interface. A virada live do Stripe também é **[S]** e não segura os demais.

Epic: [V3a](https://linear.app/career-forge-v2/issue/CAR-122).

| Trilho | Classe | Issue |
|--------|--------|-------|
| Continuity email | **Done** | [V3a: Continuity email](https://linear.app/career-forge-v2/issue/CAR-123) — PR #90. Sweep: `apps/backend/scripts/continuity_sweep.py` |
| Video References | **[P]** | [V3a: Video References](https://linear.app/career-forge-v2/issue/CAR-124) |
| Stripe copy | **[S]** | [V3a: Welcome and paywall say USD $7/mo](https://linear.app/career-forge-v2/issue/CAR-125) — depois do gate freemium, para a frase do paywall bater com ele |
| Portal + Billing email | **Done** | [V3a: Customer Portal and Billing email](https://linear.app/career-forge-v2/issue/CAR-126) — PR #91. Alembic `022_billing_email_spell` |
| Sentry DSN no deploy | **[P]** | [V3a: Pass the Sentry frontend DSN in the Labs deploy](https://linear.app/career-forge-v2/issue/CAR-127) |
| Membership no perfil | **[P]** | [V3a: Read membership from the Borderless profile](https://linear.app/career-forge-v2/issue/CAR-128) |
| Freemium | **[S]** | [V3a: One forge, then the subscription](https://linear.app/career-forge-v2/issue/CAR-130) — depois da leitura do perfil |
| Senha do Career Forge | **[P]** | [V3a: Career Forge password](https://linear.app/career-forge-v2/issue/CAR-129) |
| Dual language — interface | **Merged** | [pt-BR learner interface (i18n)](https://linear.app/career-forge-v2/issue/CAR-37) — PR #92. Alembic `023_ui_locale`. O catálogo pt-BR é rascunho; a issue não fecha antes da revisão humana |
| Emails no idioma | **[S]** | [V3a: Learner emails follow the stored locale](https://linear.app/career-forge-v2/issue/CAR-131) — depois da interface |
| Roadmap no idioma | **[S]** | [V3a: Forge roadmap in the learner locale](https://linear.app/career-forge-v2/issue/CAR-132) — depois da interface |
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

O paywall deixa de dizer “Free forge used” e “subscribe to continue”. Ele nomeia USD $7/mo para quem já gastou o forge da vida da conta e não tem assinatura. BASE e PSP não veem o painel. O texto exato é do build. Essa copy espera o gate freemium.

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

## Freemium

[V3a: Read membership from the Borderless profile](https://linear.app/career-forge-v2/issue/CAR-128) · [V3a: One forge, then the subscription](https://linear.app/career-forge-v2/issue/CAR-130) · [ADR-005](./decisions/ADR-005-identity-gate-product-entry.md)

`external` é quem tem membership FREE, quem não tem conta na Borderless, ou cujo perfil falta. Pode começar **um forge na vida da conta**, e só se nenhum forge dessa conta foi concluído. Começar gasta a franquia, mesmo se o forge falhar ou a pessoa sair. A diagnosis pode ser refeita até esse começo e faz parte desse forge. Um forge concluído também gasta, inclusive um concluído como BASE ou PSP: virar FREE depois disso leva à assinatura. Um forge de BASE ou PSP que começou e não concluiu não gasta.

Depois da franquia, começar diagnosis ou forge devolve 402 até a assinatura no Checkout do Career Forge, USD $7/mo. Cancelar não devolve outro forge grátis. A franquia é uma por conta, em qualquer goal. O Checkout aparece quando ela acaba.

BASE e PSP não passam pelo Stripe. Podem concluir 2 forges num mês UTC. O terceiro espera o mês seguinte, sem oferta de Stripe. Quem assina fica fora desse teto. O orçamento mensal global da API continua valendo para todo mundo. Um Roadmap que já existe continua aberto.

No modo senha, ter `borderless_user_id` deixa de incluir a pessoa. Só BASE e PSP entram sem cobrança.

## Membership

Cada checagem de entitlement de quem tem conta na Borderless chama `GET /api/users/profile`. O campo `membership` vale BASE, PSP ou FREE. Uma leitura que falha mantém o último rótulo que funcionou. A checagem seguinte, cinco minutos depois da falha, tenta de novo em silêncio. Fora do produto, nada dispara sozinho. O acesso da Borderless que guardamos é renovável, para a nova leitura funcionar sem pedir a senha outra vez. Se não der para renovar, o último rótulo fica até o próximo login com a senha da Borderless.

Conta só no Career Forge não tem perfil para ler e permanece `external` até um login da Borderless no mesmo e-mail.

## Conta só no Career Forge

[V3a: Career Forge password](https://linear.app/career-forge-v2/issue/CAR-129)

O primeiro acesso prova o e-mail com o OTP e define uma senha que o Career Forge guarda. Os acessos seguintes usam essa senha. O OTP do learner não é a porta de todo dia. Essa senha é outra, distinta da senha da Borderless. As duas abrem o mesmo usuário.

Esquecer a senha do Career Forge troca por um e-mail nesse endereço. A senha da Borderless não muda. O mesmo e-mail no login da Borderless é a mesma conta: a checagem seguinte lê o perfil, BASE ou PSP entram na regra incluída, FREE continua `external`, e um forge já começado continua gasto. Uma conta já ligada à Borderless pode ganhar essa senha depois.

## Dual language

[pt-BR learner interface (i18n)](https://linear.app/career-forge-v2/issue/CAR-37) · [Learner emails follow the stored locale](https://linear.app/career-forge-v2/issue/CAR-131) · [Forge roadmap in the learner locale](https://linear.app/career-forge-v2/issue/CAR-132)

Inglês é o padrão. pt-BR é opt-in. A URL não muda. `next-intl` escolhe o catálogo pelo cookie. A Welcome indexada continua a inglesa. O controle fica no chrome, Welcome incluída.

Sem login, só o cookie. No login, se a pessoa mexeu no controle, o cookie grava por cima da conta. Logada, o controle grava os dois. Sem escolha gravada, interface e email ficam em inglês.

A interface do learner entra nos catálogos, inclusive a casca de `/learn` e de Reference. O markdown da lição e o corpo de um embed de fora ficam como foram publicados. O Operator console fica em inglês. Chave pt-BR sem revisão humana cai para o inglês. A máquina pode rascunhar o catálogo. A issue não fecha antes dessa revisão.

Os emails do learner (código, continuidade, cobrança, resume) usam o idioma gravado na conta. O email do Operator fica em inglês. Mesma regra de rascunho e revisão.

O prompt do forge continua em inglês e, na largada, pede o roadmap no idioma da conta. Trocar no meio do stream não reescreve esse forge. O próximo usa o idioma novo. Um roadmap já existente não é traduzido. Diagnosis, validation e mentor continuam em inglês. O texto em pt-BR é português do Brasil.

---

## Fora da V3a

Ficam sem fase até uma decisão futura, não como V3b:

- Cobertura canônica de `/learn` além dos cinco corpos de RAG
- Cadência de mastery (quando validar / mock)
- Continuidade dentro do produto (bell, banner)
- Faixa de erros recentes no Operator

Fora deste plano: Discord, NocoDB, Job-RAG, domínio standalone, certificação, diagnosis hard-block, streaks, badges, checkout na Welcome, prompts traduzidos, diagnosis/validation/mentor em pt-BR, Stripe no Operator console, SSO além da Borderless.

---

## Aberto

[Provision Stripe Price and keys for Labs](https://linear.app/career-forge-v2/issue/CAR-121) — tarefa, não decisão. Price USD $7/mo de teste e depois live, sem trial, sem Price em BRL, Adaptive Pricing no Checkout. Segredos fora do git. É a porta das chaves live. Não segura os outros trilhos da V3a.
