# Skill graph catalog — `roadmap.json`

Static skill catalog for **Career Forge** (Backend Beginner track). Loaded into Postgres `skill_nodes` by the seed script.

## File shape

| Field | Type | Description |
|-------|------|-------------|
| `track.id` | string | Track slug (`backend-beginner`) |
| `track.title` | string | Display name |
| `categories[]` | object | UI spine labels: Fundamentos, Backend Core, Integração |
| `nodes[]` | object | Skill catalog entries (6–8 for MVP) |

### Node fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable slug (PK in DB), e.g. `http` |
| `title` | string | PT-BR display title |
| `category` | string | `fundamentos` \| `backend` \| `integracao` |
| `description` | string | Short subtitle for canvas |
| `icon` | string | Icon key for UI |
| `side` | string | `left` \| `right` — vertical roadmap layout |
| `sort_order` | int | Spine order within track |
| `prerequisites` | string[] | Other node `id`s that must precede this node |
| `outcomes` | string[] | Learning outcomes (what the learner should achieve) |
| `rubric` | string[] | Mastery validation criteria (AI interview) |

## Database mapping

```
roadmap.json nodes  →  skill_nodes (catalog, shared)
user progress       →  user_skill_nodes (status, mastery_score, evidence)
validation runs     →  validations (score, feedback, Q&A JSON)
```

### Status enum (`user_skill_nodes.status`)

`bloqueado` · `recomendado` · `em_estudo` · `validar` · `aprovado` · `revisar`

Prototype reference: [`claude-design-docs/prototype/skill-graph.jsx`](../claude-design-docs/prototype/skill-graph.jsx)

## Seed

```bash
cd apps/backend
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge
alembic upgrade head
python -m scripts.seed
python -m scripts.seed --demo-ana   # optional demo user
```

See [`apps/backend/src/career_forge/db/models/`](../apps/backend/src/career_forge/db/models/) for SQLAlchemy definitions.
