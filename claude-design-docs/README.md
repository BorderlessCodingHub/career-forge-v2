# Claude Design — Career OS

Documentação da UI gerada no Claude Design e do intent de produto por tela.

## Prototype

Arquivos exportados do Claude Design (React standalone via Babel):

| Arquivo | Conteúdo |
|---------|----------|
| [prototype/Career OS.html](./prototype/Career%20OS.html) | Entry point — abrir no browser |
| [prototype/app.jsx](./prototype/app.jsx) | Router / shell |
| [prototype/screens-flow.jsx](./prototype/screens-flow.jsx) | Onboarding + goal picker |
| [prototype/screens-forge.jsx](./prototype/screens-forge.jsx) | **Live Roadmap Forge + reveal** |
| [prototype/screens-dashboard.jsx](./prototype/screens-dashboard.jsx) | Skill graph steady state |
| [prototype/skill-graph.jsx](./prototype/skill-graph.jsx) | Grafo + nós |
| [prototype/components.jsx](./prototype/components.jsx) | Design system components |
| [prototype/styles.css](./prototype/styles.css) | Tokens + layout |

```bash
open "claude-design-docs/prototype/Career OS.html"
```

## Posicionamento visual

- **Inspirado em** [roadmap.sh](https://roadmap.sh) — minimalismo, dev-friendly, dark mode
- **Evoluído para** skill graph vivo — nós com status, dependências, mastery %
- **Não é** LMS genérico, gamificação ou clone 1:1

## Telas (fluxo demo)

| # | Rota | Nome | Wow |
|---|------|------|-----|
| 1 | `/` | Goal Picker | Objetivo + motivação |
| 2 | `/onboarding` | Diagnóstico IA | Chat 4–6 perguntas |
| 3 | `/roadmap/forge` | **Live Roadmap Forge** | Timeline streaming + grafo enchendo |
| 3b | `/roadmap/forge/complete` | Graph Reveal | Boom — trilha pronta |
| 4 | `/roadmap` | Skill Graph Dashboard | Missão + grafo steady |
| 5 | `/validate/:topic` | Mastery Validation | Entrevista + score |
| 6 | `/roadmap` (updated) | Adaptive + Mentor | Trilha reagiu pós-validação |

## Live Roadmap Forge (hero UX)

Pós-onboarding, o usuário **vê a IA trabalhar**:

**Esquerda — timeline ao vivo:**
- Pensamentos (`reasoning_delta`)
- Artefatos encontrados (`artifact_found`)
- Decisões de prioridade (`decision`)

**Direita — skill graph skeleton:**
- Nós aparecem parcialmente conforme `node_updated`
- No final: reveal animado → grafo completo

Script de demo mockado em `screens-forge.jsx` (`FORGE_SCRIPT`) — implementação real usa SSE do FastAPI + LangGraph.

## Design tokens

Ver [design-tokens.md](./design-tokens.md) e `prototype/styles.css`.

## Brief original

Ver [brief-v1.md](./brief-v1.md) — prompts usados no Claude Design.

## Handoff → Next.js

Ao implementar:

1. Extrair tokens → `tailwind.config.ts`
2. Mapear componentes → `apps/web/components/`
3. `data-screen` attributes → App Router routes
4. Forge timeline → consome `EventSource` SSE
5. Graph reveal → Framer Motion

## Stack de implementação

Front consome API FastAPI. Ver [docs/stack-and-roadmap-forge.md](../docs/stack-and-roadmap-forge.md).
