# UX Flow — Career Forge

> **Canonical flow (HAC-21).** Screen-by-screen narrative with old vs new paradigm.  
> Must-match constraints: [SCREEN-INTENT.md](./SCREEN-INTENT.md) · Hierarchy: [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md)

---

## Flow summary (source of truth)

```
Goal → Onboarding pill rounds → Editable diagnosis → [Gerar roadmap] → Forge stream (timeline only) → Animation reveal → Vertical roadmap (artifact mode)
```

**Breadcrumb mental:** Objetivo → Diagnóstico → Revisar diagnóstico → Forjar trilha → Explorar trilha

5-min demo: [CHECKPOINT](../docs/CHECKPOINT.md#demo-script-5-min)

---

## Paradigm shift (old → new)

| Aspect | Old (pre HAC-21) | New (HAC-21+) |
|--------|------------------|---------------|
| Pós-chat diagnóstico | Tela de confirmação read-only (`/onboarding/result`) — CTA "Ver minha trilha" | **Diagnóstico editável** — usuário edita/adiciona/remove itens, CTA **"Gerar roadmap"** |
| Entrada no forge | Auto-jump ou CTA passivo após confirmação | **Explícito** — só após "Gerar roadmap" |
| Forge durante stream | Split 40/60: timeline + skill graph skeleton enchendo | **Só timeline** — passos numerados 1, 2, 3, 4… (reasoning stream). **Sem grafo visível** |
| Fim do forge | Reveal inline com grafo completo + MissionBanner | **Animação** — cada frase/item do stream **voa para lugar** no layout vertical |
| Steady state pós-forge | Skill graph dashboard (nós conectados, sidebar fixa) | **`artifact` mode** — roadmap vertical full-width estilo [roadmap.sh](https://roadmap.sh); **click node → drawer** (referências + Ask AI); sem stepper nem sidebar de progresso |
| Numeração de passos | Implícita na timeline | **1–N só durante geração** — não aparece no steady state |
| App modes | Single chrome | **`setup`** (goal → forge) vs **`artifact`** (trilha pronta) |
| IA no dashboard | Mentor drawer contextual (P1) | **Ask AI** no drawer do nó (roadmap.sh tutor style); mentor full drawer = P1 opcional |

---

## Screen-by-screen

### 1. Goal Picker (`/`)

**Unchanged.** Usuário declara sonho profissional + motivação.

| | |
|---|---|
| **Old** | Hero + 3 cards + textarea motivação |
| **New** | Same |
| **Route** | `/` · `data-screen="goal-picker"` |

---

### 2. Onboarding diagnostic (`/onboarding`)

**Redesigned (HAC-24).** Pill/balloon rounds — 3 batches, 2 questions per round; not linear chat bubbles.

Short explicit negative answers (for example, **"Nada."**) are valid evidence for the Judge and must not block "Próxima rodada".

| | |
|---|---|
| **Old** | Linear chat bubbles — one Q at a time |
| **New** | Pill rounds → gera diagnóstico → **diagnóstico editável** (não confirmação passiva) |
| **Route** | `/onboarding` · `data-screen="diagnostic"` |

---

### 3. Editable diagnosis (`/onboarding/edit`) ⭐ NEW

**Replaces** read-only diagnosis confirmation screen.

**User job:** Revisar e **corrigir** o que a IA entendeu — sentir controle antes de forjar a trilha.

| | |
|---|---|
| **Old** | `/onboarding/result` — 3 blocos read-only (fortes / lacunas / recomendação), CTA "Ver minha trilha" |
| **New** | **View-first** listas editáveis: ícones editar/excluir por item, add (+), **drag-and-drop** em prioridades (dnd-kit). CTA **"Gerar roadmap"** + **"Refazer diagnóstico"** |
| **Why** | Tela de confirmação era dead-end — sem feedback, sem agency |
| **Route** | `/onboarding/edit` · `data-testid="editable-diagnosis"` |
| **Shipped** | HAC-53 — view/edit modes per item; strengths/gaps editable; priorities reorderable |
| **On confirm (target)** | `POST /diagnosis/confirm` persiste perfil no Postgres → `POST /forge` (202 + run_id) → SSE. **API:** HAC-52 ✅ · **FE wire:** HAC-57 pending |

**Sections (editable lists):**
- Pontos fortes
- Lacunas
- Recomendação / 1ª missão

---

### 4. Live Roadmap Forge (`/roadmap/forge`) ⭐ REDESIGNED

**User job:** Ver a IA **pensar** — emotional peak #1.

| | |
|---|---|
| **Old** | Split view: timeline esquerda + skill graph skeleton direita preenchendo com `node_updated` |
| **New** | **Full-width streaming timeline only.** Passos numerados (1, 2, 3, 4…). Tipos: `reasoning_delta`, `artifact_found`, `decision`. `artifact_found` pode mostrar query + fontes oficiais. **Nenhum grafo/map durante stream** |
| **Route** | `/roadmap/forge` · `data-screen="forge-stream"` |

**During generation:**
- Header: "Forjando sua trilha personalizada"
- Counter: elapsed, passos concluídos
- Pesquisa ao vivo: query + cards de fontes oficiais quando `research_enrich` roda
- Planner/evaluator: artifacts mostram criação do plano e verdict `ship|revise`; quando há revise, a IA aplica feedback antes do `graph_ready`.
- Cursor/stream tail ativo até `graph_ready`
- Após `graph_ready`, manter a timeline visível por alguns segundos antes do redirect para o reveal, para o usuário perceber pesquisa + consolidação.

**NOT during generation:**
- Skill graph preview
- Split panel com mapa
- Numeração permanente nos nós (só na timeline)

---

### 5. Animation reveal (`/roadmap/forge/complete`) ⭐ REDESIGNED

**User job:** Closure — "minha trilha existe" — transição mágica para o plano.

| | |
|---|---|
| **Old** | Grafo completo aparece no painel direito; MissionBanner; CTA explorar |
| **New** | Cada item/frase do stream **anima voando** para posição no **layout vertical roadmap**. Spine + nós left/right materializam. Sem confetti — premium dev-tool |
| **Route** | `/roadmap/forge/complete` · `data-screen="forge-reveal"` |

Após animação → navega para steady state (`/roadmap`).

---

### 6. Vertical roadmap — steady state (`/roadmap`) ⭐ ARTIFACT MODE (HAC-25)

**User job:** Explorar **artefato final** — trilha personalizada como página roadmap.sh, não tela de setup.

| | |
|---|---|
| **Old** | Stepper 01–07 + sidebar progresso/evidências/mentor + nós coloridos por status |
| **New** | **`artifact` mode:** top bar mínima (logo + trilha); canvas full-width; nós **uniformes** (roxo Borderless); **click → drawer direita** com descrição, referências, Ask AI, validar |
| **Route** | `/roadmap` · `data-screen="vertical-roadmap"` · `data-mode="artifact"` |

**References:** [roadmap-sh-reference-full.png](./references/roadmap-sh-reference-full.png) · [trail-dashboard-polluted-current.png](./references/trail-dashboard-polluted-current.png) (anti-pattern)

**Career Forge difference:** Trilha adaptativa — status/mastery aparecem no **drawer do nó**, não poluindo o canvas.

**Node drawer:**
- Título + descrição do domínio
- Seção **Referências** (links mock)
- **Perguntar à IA** — mini chat estilo roadmap.sh tutor
- CTA **Validar com IA** (quando aplicável)

---

### 7. Mastery validation (`/validate/:topic`)

**Unchanged** in flow position. Emotional peak #2.

| | |
|---|---|
| **Old** | Entrevista + ScoreRing |
| **New** | Same |
| **Route** | `/validate/:topic` · `data-screen="validation"` |

---

### 8. Adaptive roadmap (`/roadmap` updated)

**Unchanged intent.** Trilha reage após validação falha.

| | |
|---|---|
| **Old** | Graph diff + mentor drawer |
| **New** | Vertical roadmap atualiza nós/status; mentor pode ser drawer ou extensão do AI sidebar |
| **Route** | `/roadmap` · `data-screen="adaptive-state"` |

---

## Routes removed / deprecated

| Route | Status |
|-------|--------|
| `/onboarding/result` (read-only confirmation) | **Removed** — replaced by `/onboarding/edit` |

---

## Prototype drift

| Area | Status |
|------|--------|
| Artifact steady state (`#roadmap`) | ✅ HAC-25 — setup vs artifact modes, click-to-drawer |
| Forge uniform nodes | ✅ HAC-25 |
| Editable diagnosis screen | ⬜ Still hash `#result` placeholder |
| Forge timeline-only (no graph during stream) | ⬜ Prototype keeps split forge layout (user approved layout HAC-25) |

Implementation target: this doc + [SCREEN-INTENT.md](./SCREEN-INTENT.md).

---

*Last updated: HAC-25 — artifact mode paradigm*
