# Cursor Cloud — agent bootstrap

> **Agent navigation:** [← AGENTS.md](../AGENTS.md) · **Prev:** [CHECKPOINT.md](./CHECKPOINT.md) · **Next:** [AGENT-DELIVERY.md](./AGENT-DELIVERY.md)  
> **See also:** [docs index](./README.md) · [V2-PLAN.md](./V2-PLAN.md) · [end-session-smoke rule](../.cursor/rules/end-session-smoke.mdc)

Start with [CHECKPOINT.md](./CHECKPOINT.md) and [V2-PLAN.md](./V2-PLAN.md) before running Cloud workflows.

How to run Career Forge development from a **Cloud agent** that clones only this Git repo. No parent workspace folder required.

---

## 1. Clone and install

```bash
git clone <repo-url> career-forge-v2 && cd career-forge-v2
cp .env.example .env
make up
```

**Prerequisites:** Docker (Postgres + backend + frontend), Node.js 20+ (Playwright MCP locally), Python 3.12+ (backend).

---

## 2. Environment variables

Copy from `.env.example`. Do **not** commit `.env` or secrets.

| Variable | Purpose | Default (local) |
|----------|---------|-----------------|
| `DATABASE_URL` | Postgres connection | `postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge` |
| `BACKEND_URL` | API base | `http://localhost:8000` |
| `FRONTEND_URL` | Web base | `http://localhost:3300/career-forge` |
| `OPENAI_API_KEY` | LangGraph / OpenAI | — |
| `LANGSMITH_API_KEY` | LangSmith tracing | — |

---

## 3. Linear (Borderless Labs)

Workspace: [borderless-coding](https://linear.app/borderless-coding) · Team: **Borderless Labs** (`LABS01`) · Project: **Career Forge**

Query and create issues on that team and project. `CAR-*` links in living docs are the pre-migration archive. `BOR2-*` was the previous key on this team; the current identifier is `LABS01` with the same number.

**Preferred (local + Cloud):** enable the **Linear** Cursor plugin / MCP (`plugin-linear-linear`). Authenticate via Cursor’s Linear OAuth — no repo secret required.

Issue / branch format: `LABS01-XX-title-slug` (strip a `feature/` or `username/` prefix).

Optional legacy: if using HTTP Bearer MCP via [`.cursor/mcp.json.example`](../.cursor/mcp.json.example), set a personal API key in Cursor secrets and point it at the borderless-coding workspace. Do not commit keys.

---

## 4. Start the stack

```bash
make smoke
```

| Command | Purpose |
|---------|---------|
| `make up` | Start docker stack |
| `make down` | Stop stack |
| `make test` | Backend pytest |
| `make smoke` | Full harness + health checks |
| `make agent-verify` | Gate C — structure + optional `/health` |

---

## 5. Agent bootstrap order

1. [AGENTS.md](../AGENTS.md)
2. [V2-PLAN.md](./V2-PLAN.md)
3. [ROADMAP.md](./ROADMAP.md)
4. [STATUS.md](./STATUS.md)
5. [CHECKPOINT.md](./CHECKPOINT.md)
6. Linear issue (`LABS01-XX`, team Borderless Labs, project Career Forge)
7. [AGENT-DELIVERY.md](./AGENT-DELIVERY.md) before merge

AI work: also [engineering/EXECUTION-FLOW.md](./engineering/EXECUTION-FLOW.md) → [engineering/AI-EXECUTION.md](./engineering/AI-EXECUTION.md)

---

## 6. Delivery reminders

- One issue = one branch = one merge
- Triple gate: `SHIP + PASS + VERIFIED`
- After merge: Linear → **Done** manually + update STATUS / ROADMAP
- Deploy Labs: [DEPLOY-LABS-MANUAL.md](./DEPLOY-LABS-MANUAL.md)

---

*Career Forge v2 · Borderless Labs*
