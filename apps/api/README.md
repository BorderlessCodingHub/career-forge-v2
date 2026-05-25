# Career Forge API (HAC-6 schema)

FastAPI backend for skill graph, roadmap forge, and mastery validation.

## Layout

```
app/
  db/          SQLAlchemy Base + session
  models/      users, profiles, skill_nodes, user_skill_nodes, validations
  main.py      FastAPI stub (HAC-5 extends)
alembic/       migrations
scripts/       seed from data/roadmap.json
```

## Setup

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge
alembic upgrade head
python -m scripts.seed --demo-ana
```

Catalog source: [`../../data/roadmap.json`](../../data/roadmap.json) · Schema docs: [`../../data/README.md`](../../data/README.md)

## Tables

| Table | Role |
|-------|------|
| `users` | Learner identity (`external_id` for demo-ana) |
| `profiles` | Goal, motivation, diagnosis JSON |
| `skill_nodes` | Static catalog from roadmap.json |
| `user_skill_nodes` | Per-user status + mastery (graph state) |
| `validations` | AI mastery interview results |

HAC-5: wire `get_db` dependency, docker-compose Postgres, and import models from this package.
