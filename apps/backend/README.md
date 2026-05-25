# Career Forge Backend

Domain-oriented FastAPI backend. Python package: **`career_forge`** under `src/`.

## Layers

| Layer | Path | Responsibility |
|-------|------|----------------|
| **api** | `src/career_forge/api/` | Thin HTTP routers only |
| **schemas** | `src/career_forge/schemas/` | Pydantic contracts (HAC-7) |
| **graphs** | `src/career_forge/graphs/` | LangGraph state machines |
| **agents** | `src/career_forge/agents/` | LangChain prompt assembly |
| **streaming** | `src/career_forge/streaming/` | SSE adapters (graphs → HTTP) |
| **services** | `src/career_forge/services/` | Deterministic business logic |
| **db** | `src/career_forge/db/` | SQLAlchemy — **single DB entry** (`session.py`) |

## Run locally

```bash
cd apps/backend
pip install -r requirements.txt
PYTHONPATH=src uvicorn career_forge.main:app --reload
```

OpenAPI: http://localhost:8000/docs

## Tests

```bash
cd apps/backend
PYTHONPATH=src pytest -q
```

## Migrations & seed

```bash
cd apps/backend
PYTHONPATH=src alembic upgrade head
PYTHONPATH=src python -m scripts.seed --demo-ana
```

Fixtures: `src/career_forge/fixtures/` · Catalog seed: repo `data/roadmap.json`
