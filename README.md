# Career Forge v2

**Learn with hands-on validation** — an adaptive skill graph that diagnoses, forges your roadmap live, validates mastery, and generates evidence for mentors.

Borderless Labs · [labs.borderlesscoding.com/career-forge](https://labs.borderlesscoding.com/career-forge)

| Layer | Technology |
|--------|------------|
| Frontend | Next.js + TypeScript + Tailwind (App Router) |
| Backend | FastAPI + Pydantic + SQLAlchemy |
| Database | PostgreSQL |
| AI | LangGraph + LangChain + LangSmith |
| Deploy | GHCR + VPS (Docker Compose + reverse proxy) |

**Audience (v2):** BASE and PSP learners — spectrum from ~6 months XP to decades. Goals target **LLM engineer** tracks (RAG, Agents, Evals, Fine-tuning).

---

## What it is

Career Forge is an **AI-native** learning system. Without AI, the core flow stops.

**Problem:** generic roadmaps don't know where you're starting from and don't validate whether you actually learned anything.

**Solution:** a personalized roadmap inspired by [roadmap.sh](https://roadmap.sh), with an AI engine at every critical stage — diagnosis, live forge, interview-based validation, and roadmap adaptation.

Full product and architecture overview: [docs/CHECKPOINT.md](./docs/CHECKPOINT.md).

---

## Main features

- **Adaptive diagnosis (CTRR)** — multi-turn AI interview that maps where you actually start (≤2 questions per round, adaptive rubric).
- **Live Roadmap Forge** — the AI builds your personalized roadmap with visible reasoning, streamed live over SSE.
- **AI mastery validation** — interview-based validation; the roadmap reacts (unlocks/blocks nodes) to your result.
- **Adaptive memory (knowledge gaps)** — wrong answers become structured gaps that feed mock interviews, the mentor, and remediation tasks.
- **MCQ mock interview** — agent-generated questions with deterministic, server-side scoring.
- **Chapter Q&A tutor** — grounded tutor per roadmap node (key concepts + official references).
- **Contextual mentor + evidence report** — chat with full progress context and a mentor-facing evidence report.
- **Forge recovery + auth scaffold** — anonymous JWT, saved forges, share/resume tokens, and `/forges` list (pre-Borderless login).

---

## v2 goals (LLM tracks)

| Goal id | Track |
|---------|-------|
| `rag-engineer` | Production RAG & Advanced Retrieval |
| `agent-engineer` | Agent Engineering (MCP, Tool Use, Failure Modes) |
| `llm-evals` | LLM Evaluation & Observability (LLMOps) |
| `fine-tuning` | Fine-Tuning & Alignment (LoRA, DPO, Custom Models) |

---

## What the app does (flow)

1. **Goal** — choose a target and motivation (+ optional PDF CV).
2. **Diagnosis interview (CTRR)** — the AI asks up to 2 questions per round, with an adaptive rubric.
3. **Editable diagnosis** — adjust gaps and strengths before generating the roadmap.
4. **Live Roadmap Forge** — streaming in **timeline only** mode (no graph preview during generation).
5. **Vertical roadmap (artifact mode)** — post-forge steady state, vertical roadmap style.
6. **Validate with AI** — mastery interview; the roadmap reacts to the result.
7. **Contextual mentor + report** — chat with progress context and evidence for Borderless mentors.

---

## Architecture (summary)

```
apps/frontend/     Next.js (App Router: setup + artifact) · basePath /career-forge
apps/backend/      FastAPI (career_forge)
data/roadmap.json  Static skill catalog
PostgreSQL         Profiles, roadmap, diagnosis sessions, graph_runs, forge_artifacts
```

Detailed structure: [docs/engineering/REPO-STRUCTURE.md](./docs/engineering/REPO-STRUCTURE.md).

**Diagrams (module dependencies + per-feature sequence):** [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

---

## Quick start (recommended)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- OpenAI API key (required for diagnosis, forge, and validation)

### Start the stack

```bash
git clone git@github.com:BorderlessCodingHub/career-forge-v2.git
cd career-forge-v2

cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

make up
make status   # shows real URLs (frontend port comes from WEB_HOST_PORT in .env)
make smoke    # validates harness + health checks
```

| Service | Typical URL |
|---------|-------------|
| Frontend | `http://localhost:<WEB_HOST_PORT>/career-forge` (default **3300**) |
| Backend (OpenAPI) | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

Stop everything: `make down`

> **Frontend basePath:** the app is served under `/career-forge`. Use `make status` for the full URL. If 3300 is already in use, pick another port (e.g. `WEB_HOST_PORT=3000`) and add the origin to `CORS_ORIGINS`.

> **Conflict on 5432:** if another Postgres is already using port 5432 on the host, stop the other service or adjust the mapping in `docker-compose.yml` before `make up`.

---

## Essential environment variables

Copy [.env.example](./.env.example) to `.env` and fill in at least:

| Variable | Required | Use |
|----------|----------|-----|
| `OPENAI_API_KEY` | **Yes** (AI) | Diagnosis, forge, validation, mock interview |
| `DATABASE_URL` | Yes (Docker fills it in) | Postgres |
| `CORS_ORIGINS` | Yes | Must include the frontend URL (`http://localhost:3300`, etc.) |
| `NEXT_PUBLIC_BACKEND_URL` | Yes | Frontend → API |
| `NEXT_PUBLIC_API_URL` | Yes | Same |
| `WEB_HOST_PORT` | Yes (local) | Published Next.js port on the host |
| `FRONTEND_URL` | Yes (local) | e.g. `http://localhost:3300/career-forge` |
| `JWT_SECRET` | Yes (shared deploy) | Anonymous auth scaffold (change in production) |
| `LANGSMITH_API_KEY` | No | LLM trace observability |
| `LANGSMITH_PROJECT` | No | LangSmith project (e.g. `career-forge`) |

Labs production: [docs/DEPLOY-LABS-MANUAL.md](./docs/DEPLOY-LABS-MANUAL.md).

---

## Quick demo flow (~5 min)

With the stack running (`make up`):

1. Open the frontend (`make status` → URL with `/career-forge`).
2. Set your goal and motivation; optionally attach a CV.
3. Complete the diagnosis interview (pills/text from the API).
4. In **editable diagnosis**, adjust gaps and click **Generate roadmap**.
5. Watch the **Forge** (SSE timeline) until the reveal → vertical roadmap.
6. Open a node → **Validate with AI** → watch the score and the roadmap react.
7. (Optional) Mentor / report on the roadmap.

Script aligned with [docs/CHECKPOINT.md](./docs/CHECKPOINT.md) § Demo script.

---

## Useful commands

| Command | Description |
|---------|-------------|
| `make up` | Starts postgres + backend + frontend (builds if needed) |
| `make down` | Stops the stack |
| `make status` | Compose status + URLs |
| `make smoke` | Harness + health checks |
| `make test` | Bootstrap Postgres + Alembic upgrade + backend pytest |
| `make seed` | Seed the catalog + demo user Ana |
| `make agent-verify` | Structure Gate C + optional `/health` |
| `make golden-check` | Deterministic golden case suite (CAR-18) |
| `make must-have-coverage` | Must-have node coverage harness (CAR-17) |
| `make cost-gate` | Synthetic cost gate + Yuri report (CAR-7) |

---

## Development without Docker (optional)

Useful for fine-grained backend debugging or running the frontend in isolation.

```bash
# Terminal 1 — Postgres only
docker compose up -d postgres

# Terminal 2 — Backend
cd apps/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge
export OPENAI_API_KEY=sk-...
PYTHONPATH=src uvicorn career_forge.main:app --reload --port 8000

# Terminal 3 — Frontend (at the repo root, using the root .env)
cd apps/frontend
pnpm install && pnpm dev
```

Make sure `CORS_ORIGINS`, `FRONTEND_URL`, and `NEXT_PUBLIC_*` in the root `.env` point to the port where Next starts.

---

## Deploy (production)

| Environment | How |
|-------------|-----|
| **Labs (primary)** | [labs.borderlesscoding.com/career-forge](https://labs.borderlesscoding.com/career-forge) · path `/career-forge` · auto-deploy on push to `main` |
| Images | `ghcr.io/borderlesscodinghub/career-forge-{backend,frontend}` |
| CI/CD | [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml) |

Full runbook: [docs/DEPLOY-LABS-MANUAL.md](./docs/DEPLOY-LABS-MANUAL.md).

---

## Documentation

| For whom | Where to start |
|-----------|----------------|
| **New to the project** | [docs/CHECKPOINT.md](./docs/CHECKPOINT.md) — complete overview |
| **v2 plan & decisions** | [docs/V2-PLAN.md](./docs/V2-PLAN.md) |
| **Current work** | [docs/ROADMAP.md](./docs/ROADMAP.md) · [docs/STATUS.md](./docs/STATUS.md) |
| **Architecture (diagrams)** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) |
| **Docs index** | [docs/README.md](./docs/README.md) |
| **Agents / contributing** | [AGENTS.md](./AGENTS.md) · [docs/AGENT-DELIVERY.md](./docs/AGENT-DELIVERY.md) |
| **AI / LangGraph** | [docs/engineering/EXECUTION-FLOW.md](./docs/engineering/EXECUTION-FLOW.md) |
| **CTRR diagnosis** | [docs/product/DIAGNOSIS-INTERVIEW.md](./docs/product/DIAGNOSIS-INTERVIEW.md) |
| **Design / UI** | [claude-design-docs/](./claude-design-docs/) (prototype + tokens) |

### UI prototype (visual reference)

Not the production app — it's for tokens and components:

```bash
cd claude-design-docs/prototype
python3 -m http.server 8765
# http://localhost:8765/
```

---

## Common problems

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| `failed to fetch` in the browser | CORS or backend down | Check that `CORS_ORIGINS` includes the frontend URL; `docker compose logs backend` |
| Diagnosis/forge not responding | `OPENAI_API_KEY` empty | Fill it in `.env` and `make down && make up` |
| Postgres won't start | Port 5432 in use | Free the port or adjust `docker-compose.yml` |
| Frontend on the wrong port | `WEB_HOST_PORT` | Use `make status` and open the displayed URL |
| 404 on `/health` locally | Missing basePath | App lives at `/career-forge`; API health is at `:8000/health` |
| Backend tests fail with `connection refused` on `localhost:5432` | Postgres wasn't running before pytest | Use `make test` (starts postgres, waits for readiness, runs `alembic upgrade head`) |

More recipes: [.cursor/skills/local-debug/SKILL.md](./.cursor/skills/local-debug/SKILL.md).

---

## Team

**Borderless Labs** · [Borderless Coding Hub](https://github.com/BorderlessCodingHub)

Career Forge v2 is maintained as part of the Borderless learning platform for BASE and PSP learners.

| Area | Lead |
|------|------|
| v2 product & engineering | [Pedro Alano](https://github.com/pedroalano) |
| AI / LangGraph motor | [Matheus Oliveira](https://github.com/MatheusOliveiraSilva) |
| Frontend (original app) | [Arthur Araujo](https://github.com/Tute24) |

## Origins

The AI-native motor (diagnosis → forge → validation) was first built by **Programadores Sem Pátria** during **HB01-2026** (BASE Mentorship): [`HB01-2026_soft-push`](https://github.com/ProgramadoresSemPatria/HB01-2026_soft-push).  
This repository is the v2 continuation: [`BorderlessCodingHub/career-forge-v2`](https://github.com/BorderlessCodingHub/career-forge-v2).
