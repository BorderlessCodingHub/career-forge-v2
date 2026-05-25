# Career Forge API (HAC-6 schema + HAC-5 runtime)

FastAPI backend for skill graph, roadmap forge, and mastery validation.

## Layout

```
app/
  config.py    Settings (CORS, DATABASE_URL)
  db/          SQLAlchemy Base + session (HAC-6)
  models/      users, profiles, skill_nodes, user_skill_nodes, validations
  routers/     /health (HAC-5)
  main.py      FastAPI app + CORS + OpenAPI /docs
alembic/       migrations
scripts/       seed from data/roadmap.json
```

## Setup (local)

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export DATABASE_URL=postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge
alembic upgrade head
python -m scripts.seed --demo-ana
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

OpenAPI: http://localhost:8000/docs · Health: http://localhost:8000/health

Catalog source: [`../../data/roadmap.json`](../../data/roadmap.json) · Schema docs: [`../../data/README.md`](../../data/README.md)

## Tables

| Table | Role |
|-------|------|
| `users` | Learner identity (`external_id` for demo-ana) |
| `profiles` | Goal, motivation, diagnosis JSON |
| `skill_nodes` | Static catalog from roadmap.json |
| `user_skill_nodes` | Per-user status + mastery (graph state) |
| `validations` | AI mastery interview results |

## Extension points

| Path | Owner issue |
|------|-------------|
| `app/schemas/` | HAC-7 — Pydantic + LangGraph contracts |
| `app/routers/` | HAC-8+ — identity, forge, validation routes |

## Deploy

Railway: see repo [`railway.toml`](../../railway.toml). Set `DATABASE_URL`, `CORS_ORIGINS`, and AI keys from root `.env.example`.
