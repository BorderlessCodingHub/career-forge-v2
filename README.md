# Career Forge

**Aprender com validação prática** — trilha viva para quem está virando dev.

Hackathon Borderless BASE 01/2026 · repo `HB01-2026_soft-push` (Soft Push)

## Problema

Roadmaps genéricos não sabem de onde você parte nem validam se você realmente aprendeu.

## Solução

Skill graph adaptativo inspirado em [roadmap.sh](https://roadmap.sh), com IA como motor:

- Diagnóstico personalizado (Identity Engine)
- **Live Roadmap Forge** — streaming do raciocínio enquanto monta a trilha
- Validação de mastery por entrevista IA
- Trilha reativa + evidências para mentores Borderless

## Stack

| Camada | Tech |
|--------|------|
| Frontend | Next.js + TypeScript + Tailwind |
| Backend | FastAPI + Pydantic + SQLAlchemy |
| DB | PostgreSQL |
| AI | LangGraph + LangChain + LangSmith |
| Deploy | Vercel (web) + Railway/Render (api) |

## Docs

| Path | Conteúdo |
|------|----------|
| [AGENTS.md](./AGENTS.md) | Índice para agentes Cursor |
| [docs/](./docs/) | ROADMAP, STATUS, CHECKPOINT, delivery gates |
| [claude-design-docs/](./claude-design-docs/) | UI prototype + design intent |

## Prototype UI

Abrir localmente:

```bash
cd claude-design-docs/prototype
python3 -m http.server 8765
open http://localhost:8765/
```

## Como rodar (em construção)

```bash
make smoke   # stub até apps/web + apps/api existirem
```

## Equipe

Programadores Sem Pátria — Hackathon BASE 2026.

## Créditos

Projeto desenvolvido no HB01-2026 (Mentoria BASE).
