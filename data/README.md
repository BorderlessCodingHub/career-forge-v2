# Skill graph catalog — `data/catalog/`

Static skill catalogs for **Career Forge** LLM tracks. Loaded into Postgres `skill_nodes` by the seed script.

## Layout

```
data/catalog/
  rag-engineer-beginner.json
  agent-engineer-beginner.json
  llm-evals-beginner.json
  fine-tuning-beginner.json
```

Each file is one track (same shape as the former single `roadmap.json`).

## File shape

| Field | Type | Description |
|-------|------|-------------|
| `track.id` | string | Track slug (e.g. `rag-engineer-beginner`) |
| `track.title` | string | Display name |
| `categories[]` | object | UI spine labels |
| `nodes[]` | object | Skill catalog entries (6–8 for MVP) |

### Node fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable slug (PK in DB) — globally unique across tracks |
| `title` | string | Display title |
| `category` | string | Category id from `categories` |
| `description` | string | Short subtitle for canvas |
| `icon` | string | Icon key for UI |
| `side` | string | `left` \| `right` — vertical roadmap layout |
| `sort_order` | int | Spine order within track |
| `prerequisites` | string[] | Other node `id`s that must precede this node |
| `outcomes` | string[] | Learning outcomes |
| `rubric` | string[] | Mastery validation criteria |

## Database mapping

```
catalog/*.json nodes  →  skill_nodes (catalog, shared; keyed by node id)
user progress         →  user_skill_nodes (status, mastery_score, evidence)
validation runs       →  validations (score, feedback, Q&A JSON)
```

### Status enum (`user_skill_nodes.status`)

`bloqueado` · `recomendado` · `em_estudo` · `validar` · `aprovado` · `revisar`

## Seed

```bash
cd apps/backend
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge
alembic upgrade head
python -m scripts.seed                 # all tracks under data/catalog/
python -m scripts.seed --demo-ana      # optional demo user
```

Env overrides:

| Var | Purpose |
|-----|---------|
| `CATALOG_DIR` | Directory of `*.json` track files (Docker: `/data/catalog`) |
| `ROADMAP_JSON_PATH` | Single-file override (tests / legacy) |

See [`apps/backend/src/career_forge/db/models/`](../apps/backend/src/career_forge/db/models/) for SQLAlchemy definitions.
