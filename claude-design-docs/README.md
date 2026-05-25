# Claude Design — Career Forge

Documentação da UI gerada no Claude Design, intent de produto por tela, e **fonte de verdade** para agentes que implementam front-end.

---

## Start here (agents)

| Doc | Purpose |
|-----|---------|
| **[PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md)** | **Canonical** — hierarchy, flow summary, implementation notes |
| **[UX-FLOW.md](./UX-FLOW.md)** | Screen-by-screen flow + old vs new paradigm (HAC-21) |
| **[SCREEN-INTENT.md](./SCREEN-INTENT.md)** | Per-screen must-match constraints |
| [PRODUCT-VISION.md](./PRODUCT-VISION.md) | North star, pillars, demo narrative |
| [UI-PRINCIPLES.md](./UI-PRINCIPLES.md) | Visual DNA, tokens, component patterns |
| [SCREEN-INTENT-MAP.md](./SCREEN-INTENT-MAP.md) | Route table + quick reference |

**Before UI work:** read PRODUCT-SOURCE-OF-TRUTH → UX-FLOW → SCREEN-INTENT → open [steady-state reference](./references/roadmap-sh-vertical-ai-tutor.png) → read [docs/CHECKPOINT.md](../docs/CHECKPOINT.md).

**After UI paradigm change:** update PRODUCT-SOURCE-OF-TRUTH (rule: [.cursor/rules/ui-product-sync.mdc](../.cursor/rules/ui-product-sync.mdc), skill: [.cursor/skills/ui-product-sync/SKILL.md](../.cursor/skills/ui-product-sync/SKILL.md)).

---

## Canonical flow (HAC-21)

```
Goal → Onboarding chat → Editable diagnosis → [Gerar roadmap] → Forge stream (steps only) → Animation reveal → Vertical roadmap + optional AI sidebar
```

Detalhes: [UX-FLOW.md](./UX-FLOW.md)

---

## Prototype

Arquivos exportados do Claude Design (React standalone via Babel):

| Arquivo | Conteúdo |
|---------|----------|
| [prototype/Career Forge.html](./prototype/Career%20Forge.html) | Entry point — abrir no browser |
| [prototype/app.jsx](./prototype/app.jsx) | Router / shell |
| [prototype/screens-flow.jsx](./prototype/screens-flow.jsx) | Onboarding + goal picker + diagnosis result (legacy) |
| [prototype/screens-forge.jsx](./prototype/screens-forge.jsx) | Live Roadmap Forge + reveal (legacy split layout) |
| [prototype/screens-dashboard.jsx](./prototype/screens-dashboard.jsx) | Skill graph steady state (legacy) |
| [prototype/skill-graph.jsx](./prototype/skill-graph.jsx) | Grafo + nós |
| [prototype/components.jsx](./prototype/components.jsx) | Design system components |
| [prototype/styles.css](./prototype/styles.css) | Tokens + layout |

```bash
open "claude-design-docs/prototype/Career Forge.html"
```

### Prototype drift

> **HAC-21:** O prototype HTML reflete o paradigma **antigo** (confirmação read-only, forge split com grafo, dashboard em skill graph). Use-o para **tokens e componentes**, não para fluxo ou layout steady state.

| Aspecto | Prototype (legacy) | Docs (HAC-21 truth) |
|---------|-------------------|---------------------|
| Pós-diagnóstico | Read-only result | Editable diagnosis + "Gerar roadmap" |
| Forge | Timeline + graph skeleton | Timeline only |
| Steady state | Skill graph dashboard | Vertical roadmap + optional AI sidebar |

Atualizar prototype: issue futura (HAC-9 / HAC-18 UI).

---

## Posicionamento visual

- **Inspirado em** [roadmap.sh](https://roadmap.sh) — layout vertical, spine central, categorias, AI tutor sidebar opcional
- **Evoluído para** skill graph adaptativo — nós personalizados com status, dependências, mastery %
- **Não é** LMS genérico, gamificação ou clone 1:1

Referência visual: [references/roadmap-sh-vertical-ai-tutor.png](./references/roadmap-sh-vertical-ai-tutor.png)

Detalhes: [UI-PRINCIPLES.md](./UI-PRINCIPLES.md)

---

## Telas (fluxo demo — HAC-21)

| # | Rota | Nome | Wow |
|---|------|------|-----|
| 1 | `/` | Goal Picker | Objetivo + motivação |
| 2 | `/onboarding` | Diagnóstico IA | Chat 4–6 perguntas |
| 3 | `/onboarding/edit` | **Diagnóstico editável** | User corrige fortes/lacunas |
| 4 | `/roadmap/forge` | **Live Roadmap Forge** | Timeline streaming (passos 1–N) — sem grafo |
| 4b | `/roadmap/forge/complete` | **Animation reveal** | Items voam para layout vertical |
| 5 | `/roadmap` | **Vertical roadmap** | Trilha steady + AI sidebar opcional |
| 6 | `/validate/:topic` | Mastery Validation | Entrevista + score |
| 7 | `/roadmap` (updated) | Adaptive + Mentor | Trilha reagiu pós-validação |

Intent completo: [SCREEN-INTENT.md](./SCREEN-INTENT.md) · [UX-FLOW.md](./UX-FLOW.md)

---

## Live Roadmap Forge (hero UX — HAC-21)

Pós-diagnóstico editável, usuário clica **"Gerar roadmap"** e **vê a IA pensar**:

**Durante geração — só timeline:**
- Passos numerados 1, 2, 3, 4…
- Pensamentos (`reasoning_delta`)
- Artefatos (`artifact_found`)
- Decisões (`decision`)
- **Sem skill graph visível**

**Ao completar:**
- Animação — cada item do stream voa para o layout vertical
- Transição para steady state em `/roadmap`

Script mockado em `screens-forge.jsx` (`FORGE_SCRIPT`) — implementação real usa SSE do FastAPI + LangGraph. UI consome timeline only; `node_updated` alimenta estado backend, não preview visual durante stream.

Spec: [docs/stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md)

---

## Design tokens

Ver [design-tokens.md](./design-tokens.md) e `prototype/styles.css`.

---

## Brief original

Ver [brief-v1.md](./brief-v1.md) — prompts usados no Claude Design (pré HAC-21).

---

## Handoff → Next.js

Ao implementar:

1. Extrair tokens → `tailwind.config.ts`
2. Mapear componentes → `apps/web/components/`
3. Seguir rotas de [UX-FLOW.md](./UX-FLOW.md) — não hash routes legacy do prototype
4. Forge timeline → consome `EventSource` SSE (timeline only)
5. Reveal → Framer Motion (items → vertical roadmap positions)
6. Steady state → vertical roadmap layout + collapsible AI sidebar

Registrar divergências em [PRODUCT-SOURCE-OF-TRUTH.md](./PRODUCT-SOURCE-OF-TRUTH.md) → Implementation notes.

---

## Stack de implementação

Front consome API FastAPI. Ver [docs/stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md) · Produto: [docs/CHECKPOINT.md](../docs/CHECKPOINT.md)
