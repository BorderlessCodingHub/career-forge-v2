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

## Como rodar localmente

### Pré-requisitos

- Docker + Docker Compose
- Node 20+ e [pnpm](https://pnpm.io/) (opcional — dev fora do Docker)
- Python 3.11+ (opcional — dev da API fora do Docker)

### Stack completa (recomendado)

```bash
cp .env.example .env
make up          # postgres + api + web
make status      # URLs
make smoke       # valida harness + health checks (sobe docker se necessário)
```

| Serviço | URL |
|---------|-----|
| Web | http://localhost:3000 |
| API OpenAPI | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

Parar: `make down`

Se a porta 3000 estiver ocupada: `WEB_HOST_PORT=3300 make up` (web em http://localhost:3300).

### Dev sem Docker (API + Postgres local)

```bash
# Terminal 1 — Postgres via docker só do banco
docker compose up -d postgres

# Terminal 2 — API
cd apps/api
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 — Web
cd apps/web
cp .env.example .env.local
pnpm install && pnpm dev
```

### Deploy (skeleton)

| App | Plataforma | Config |
|-----|------------|--------|
| `apps/web` | Vercel | `vercel.json` (root directory `apps/web`) |
| `apps/api` | Railway | `railway.toml` + env `DATABASE_URL`, `CORS_ORIGINS` |

Variáveis compartilhadas: ver `.env.example` (`OPENAI_API_KEY`, `LANGSMITH_*`).

## Equipe

Programadores Sem Pátria — Hackathon BASE 2026.

## Créditos

Projeto desenvolvido no HB01-2026 (Mentoria BASE).
