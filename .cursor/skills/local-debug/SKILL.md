---
name: local-debug
description: Use when debugging local failures, failed to fetch, API errors, Docker stack issues. Always apply for bug reports and runtime errors in Career Forge.
---

# Local debug (Career Forge)

Systematic checklist for **local dev** failures: `failed to fetch`, CORS, Docker, API 4xx/5xx, LLM flows.

---

## 1. Stack status

```bash
cd /path/to/HB01-2026_soft-push
docker compose ps
make status   # if available
```

| Service  | Host port | Internal | Health |
|----------|-----------|----------|--------|
| frontend | `${WEB_HOST_PORT:-3300}` → 3000 | — | Next dev |
| backend  | 8000 | backend:8000 | `GET /health` |
| postgres | 5432 | postgres:5432 | `pg_isready` |

Start / restart:

```bash
docker compose up -d --build
docker compose restart backend frontend
```

---

## 2. Log inspection

**Docker (primary):**

```bash
docker compose logs backend --tail 100
docker compose logs frontend --tail 50
docker compose logs postgres --tail 30
```

Watch live during repro:

```bash
docker compose logs -f backend
```

**Local log files** (only when `ENV=local` or `DEBUG=true` on backend):

- `logs/backend.log` — structured Python logs from FastAPI startup onward
- Created automatically; directory is gitignored except `.gitkeep`

Frontend: fetch errors log to browser **Console**; improved messages in `api-client.ts` mention CORS and `backendUrl`.

---

## 3. CORS / "failed to fetch"

Browser `TypeError: Failed to fetch` on POST often means **CORS preflight failed** (OPTIONS 400), not a missing route.

**Verify preflight:**

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X OPTIONS \
  "http://localhost:8000/diagnosis/interview/start" \
  -H "Origin: http://localhost:3300" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

Expect **200**. If **400**, add the browser origin to `CORS_ORIGINS` in `.env`:

```bash
# Must match WEB_HOST_PORT (common: 3300)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3300,http://127.0.0.1:3300
```

Restart backend after `.env` change: `docker compose up -d backend`.

**API URL:** frontend uses `NEXT_PUBLIC_BACKEND_URL` / `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`). In Docker, browser calls **host** port 8000, not `backend:8000`.

---

## 4. API smoke (diagnosis interview)

```bash
# Health
curl -s http://localhost:8000/health | jq .

# Start interview (requires OPENAI_API_KEY in .env)
curl -s -X POST http://localhost:8000/diagnosis/interview/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "debug-user",
    "goal_id": "backend",
    "motivation": "Quero crescer como backend engineer com foco em APIs.",
    "years_xp": "1-3"
  }' | jq .
```

---

## 5. Environment checklist

| Variable | Purpose |
|----------|---------|
| `WEB_HOST_PORT` | Host port for frontend (3300 common) |
| `CORS_ORIGINS` | Must include `http://localhost:<WEB_HOST_PORT>` |
| `BACKEND_URL` / `NEXT_PUBLIC_BACKEND_URL` | `http://localhost:8000` |
| `OPENAI_API_KEY` | Required for diagnosis interview LLM |
| `DATABASE_URL` | Postgres connection |
| `ENV=local` / `DEBUG=true` | Enables `logs/backend.log` |

Copy template: `.env.example` → `.env`. Never commit `.env`.

---

## 6. LangSmith (LLM traces)

After API reaches backend but LLM misbehaves:

```bash
./scripts/langsmith-env.sh
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --last-n-minutes 30 --error
```

Full workflow: [langsmith-inspect skill](../langsmith-inspect/SKILL.md).

---

## 7. Backend tests

```bash
make test
# or
docker compose exec backend pytest
```

---

## 8. Common fixes (discovered in repo)

| Symptom | Cause | Fix |
|---------|-------|-----|
| `failed to fetch` on onboarding step 2 | CORS preflight 400 — frontend on :3300, `CORS_ORIGINS` missing that origin | Add `:3300` origins to `.env`, restart backend |
| OPTIONS 400 in backend logs | Same as above | `docker compose logs backend \| grep OPTIONS` |
| Interview 500 | Missing `OPENAI_API_KEY` | Set in `.env`, restart backend |
| Frontend can't reach API | Wrong `NEXT_PUBLIC_BACKEND_URL` | Must be host URL, not Docker service name |

**When you find a new local-only trick, append it to section 8 of this skill.**
