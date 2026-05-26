# Cursor Cloud — agent bootstrap

> **Agent navigation:** [← AGENTS.md](../AGENTS.md) · **Prev:** [CHECKPOINT.md](./CHECKPOINT.md) · **Next:** [AGENT-DELIVERY.md](./AGENT-DELIVERY.md)  
> **See also:** [docs index](./README.md) · [end-session-smoke rule](../.cursor/rules/end-session-smoke.mdc)

Start with [CHECKPOINT.md](./CHECKPOINT.md) for the complete application overview before running Cloud workflows.

How to run Career Forge development from a **Cloud agent** that clones only this Git repo. No parent workspace folder required.

---

## 1. Clone and install

```bash
git clone <repo-url> HB01-2026_soft-push && cd HB01-2026_soft-push
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
| `FRONTEND_URL` | Web base | `http://localhost:3000` |
| `OPENAI_API_KEY` | LangGraph / OpenAI | — |
| `LANGSMITH_API_KEY` | LangSmith tracing | — |

**Linear MCP (not in app runtime — Cursor only):**

| Variable | Set by |
|----------|--------|
| `HACKATON_LINEAR_API_KEY` | [Cursor Cloud secrets](#3-cursor-dashboard-secrets) or local shell / `.env` for `${env:…}` interpolation |

---

## 3. Cursor dashboard secrets

Add `HACKATON_LINEAR_API_KEY` so Cloud agents resolve `${env:HACKATON_LINEAR_API_KEY}` in [`.cursor/mcp.json`](../.cursor/mcp.json).

### Where to configure

| Step | Location |
|------|----------|
| 1 | Open [cursor.com/dashboard/cloud-agents](https://cursor.com/dashboard/cloud-agents) |
| 2 | Select the **Secrets** tab (or **Environment variables** in environment setup) |
| 3 | Add secret: name `HACKATON_LINEAR_API_KEY`, value = Linear **Personal API key** |
| 4 | Type: **Runtime Secret** (recommended — redacted from agent transcripts) |
| 5 | Restart any running Cloud agent after adding or rotating the key |

**MCP bootstrap:** Cloud agents also pick up MCP servers from committed `.cursor/mcp.json` in the repo. You can manage additional servers from [cursor.com/agents](https://cursor.com/agents) → **MCP** dropdown. Team plans may use [cursor.com/dashboard/integrations](https://cursor.com/dashboard/integrations).

### Linear API key source

1. Linear → **Settings** → **Account** → **API** → **Personal API keys**
2. Create a key with access to the **hackas-borderless** workspace (HAC-XX issues)
3. Paste the key value only into Cursor secrets — never commit it

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

**On success:**

- Web: http://localhost:3000
- API: http://localhost:8000/health

---

## 5. MCP servers

**Linear (HTTP)** is committed in [`.cursor/mcp.json`](../.cursor/mcp.json). Merge with user-level `~/.cursor/mcp.json` or Cloud project MCP settings as needed.

### Linear MCP (recommended for issue workflow)

Use committed [`.cursor/mcp.json`](../.cursor/mcp.json) or enable **user-linear** in Cursor settings. Set `HACKATON_LINEAR_API_KEY` in Cloud secrets for Bearer auth. Tools: `list_issues`, `get_issue`, `save_issue`, branch naming for `HAC-XX` workflow.

Exact config:

```json
{
  "mcpServers": {
    "linear": {
      "url": "https://mcp.linear.app/mcp",
      "headers": {
        "Authorization": "Bearer ${env:HACKATON_LINEAR_API_KEY}"
      }
    }
  }
}
```

### Playwright MCP (Gate B — browser QA)

Optional locally; add to `~/.cursor/mcp.json` or merge from [`.cursor/mcp.json.example`](../.cursor/mcp.json.example):

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

Cloud agents: configure Playwright in **cursor.com/agents** MCP dropdown if Gate B runs in Cloud VM.

---

## Linear MCP on Cursor Mobile / Cloud

### OAuth vs API key

| Approach | Where | When to use |
|----------|--------|-------------|
| **OAuth** | Cursor Mobile / desktop UI | Default when adding Linear from MCP settings (`needauth` → **Connect**). |
| **API key + Bearer header** | Cloud agents, Mobile when OAuth redirect fails | Set `HACKATON_LINEAR_API_KEY` in **Cursor Cloud secrets** (and locally for interpolation). Never commit the key. |

This repo ships [`.cursor/mcp.json`](../.cursor/mcp.json) (and [`.cursor/mcp.json.example`](../.cursor/mcp.json.example)) with Linear's hosted MCP URL and Bearer auth via env var.

### Mobile: Connect when `needauth`

1. Open the agent chat that needs Linear (issues, branch names, etc.).
2. If Linear MCP shows **needs auth** / `needauth`, tap **Connect** and complete Linear OAuth.
3. Retry the tool call after connection succeeds.

If OAuth redirect fails, use the **Bearer workaround**: ensure `HACKATON_LINEAR_API_KEY` is in Cloud secrets and `.cursor/mcp.json` is present in the cloned repo.

### Limitations on Mobile

| Server | Mobile / Cloud agent |
|--------|----------------------|
| **Linear** (HTTP + env Bearer) | Supported when secrets + `.cursor/mcp.json` are configured |
| **Playwright** (`npx` stdio) | Not available on Mobile — use desktop or Cloud VM with Node |

---

## 6. Linear delivery workflow

**Branch format:**

```
HAC-XX-title-slug
```

Example: `HAC-18-live-roadmap-forge-langgraph-streaming`

**One issue = one branch = one merge** (~200–500 LOC).

Before merge (all mandatory):

1. `make test`
2. `make smoke` if runtime touched
3. Triple QA gate — see [AGENT-DELIVERY.md](./AGENT-DELIVERY.md)

After merge: **manual** Linear Done — see [end-task-workflow](../.cursor/rules/end-task-workflow.mdc).

Full rule: `.cursor/rules/linear-delivery-workflow.mdc`

---

## 7. Related docs

Doc catalog: [docs/README.md](./README.md). Workflow chain continues at [AGENT-DELIVERY.md](./AGENT-DELIVERY.md).

---

## 8. What cannot live in the repo

| Item | Where it lives |
|------|----------------|
| `.env` secrets | Local / Cloud env vars |
| User MCP JSON path | `~/.cursor/mcp.json` (local), repo [`.cursor/mcp.json`](../.cursor/mcp.json) (Linear HTTP), Cloud MCP merge |
| `HACKATON_LINEAR_API_KEY` | [cursor.com/dashboard/cloud-agents](https://cursor.com/dashboard/cloud-agents) Secrets — never in git |
| Docker Desktop | Host machine (Cloud VM must have Docker for `make up`) |

---

*Last updated: 2026-05-26*
