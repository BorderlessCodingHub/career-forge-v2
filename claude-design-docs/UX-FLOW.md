# UX Flow — Career Forge

> **Canonical flow (HAC-21).** Screen-by-screen narrative with old vs new paradigm.  
> Must-match constraints: [SCREEN-INTENT.md](./SCREEN-INTENT.md) · Hierarchy: [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md)

---

## Flow summary (source of truth)

```
Goal → Onboarding chat → Editable diagnosis → [Gerar roadmap] → Forge stream (steps only) → Animation reveal → Vertical roadmap (roadmap.sh) + optional AI sidebar
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
| Steady state pós-forge | Skill graph dashboard (nós conectados, sidebar fixa) | **Roadmap vertical** estilo [roadmap.sh](https://roadmap.sh) — spine central, nós esquerda/direita, categorias. **Sidebar IA opcional** (Explain, Test knowledge, Chat) |
| Numeração de passos | Implícita na timeline | **1–N só durante geração** — não aparece no steady state |
| IA no dashboard | Mentor drawer contextual (P1) | **AI Tutor sidebar opcional** — usuário escolhe falar com IA ou não |

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

### 2. Onboarding chat (`/onboarding`)

**Unchanged.** Chat diagnóstico 4–6 perguntas; IA mapeia sinais.

| | |
|---|---|
| **Old** | Chat → gera diagnóstico → vai para tela de resultado |
| **New** | Chat → gera diagnóstico → vai para **diagnóstico editável** (não confirmação passiva) |
| **Route** | `/onboarding` · `data-screen="diagnostic"` |

---

### 3. Editable diagnosis (`/onboarding/edit`) ⭐ NEW

**Replaces** read-only diagnosis confirmation screen.

**User job:** Revisar e **corrigir** o que a IA entendeu — sentir controle antes de forjar a trilha.

| | |
|---|---|
| **Old** | `/onboarding/result` — 3 blocos read-only (fortes / lacunas / recomendação), CTA "Ver minha trilha" |
| **New** | Lista estruturada **editável**: editar item, adicionar item, remover item. Perfil badge + evidence callout. CTA primário: **"Gerar roadmap"** |
| **Why** | Tela de confirmação era dead-end — sem feedback, sem agency |
| **Route** | `/onboarding/edit` · `data-screen="diagnosis-editable"` |

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
| **New** | **Full-width streaming timeline only.** Passos numerados (1, 2, 3, 4…). Tipos: `reasoning_delta`, `artifact_found`, `decision`. **Nenhum grafo/map durante stream** |
| **Route** | `/roadmap/forge` · `data-screen="forge-stream"` |

**During generation:**
- Header: "Forjando sua trilha personalizada"
- Counter: elapsed, passos concluídos
- Cursor/stream tail ativo até `graph_ready`

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

### 6. Vertical roadmap — steady state (`/roadmap`) ⭐ REDESIGNED

**User job:** Orientar o dia a dia — explorar trilha personalizada adaptativa.

| | |
|---|---|
| **Old** | Skill graph hero (~7 nós conectados), sidebar fixa com progresso/evidence |
| **New** | **Roadmap vertical** inspirado em roadmap.sh — spine central, categorias (ex. Introduction, Version Control), nós alternando esquerda/direita, status por nó. **Sidebar IA opcional** (colapsável): Explain, Test knowledge, Chat |
| **Route** | `/roadmap` · `data-screen="vertical-roadmap"` |

**Reference layout:** [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png)

**Career Forge difference:** Trilha é **adaptativa e personalizada** — não checklist estático. Status enums, mastery %, validação e replanejamento continuam.

**AI sidebar (optional):**
- Usuário **escolhe** abrir/fechar — não é chat full-screen obrigatório
- Contexto: tópico selecionado no roadmap
- Ações: Explicar, Testar conhecimento, Chat livre

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

Current HTML prototype (`prototype/`) still reflects **old** paradigm (split forge, read-only diagnosis result, graph dashboard). Treat as **visual reference for tokens/components**, not flow truth.

Implementation target: this doc + [SCREEN-INTENT.md](./SCREEN-INTENT.md). Update prototype in a future UI issue (HAC-9 / HAC-18).

See [README § Prototype drift](./README.md#prototype-drift).

---

*Last updated: HAC-21 — UX paradigm shift*
