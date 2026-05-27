# Local Debug — Runtime troubleshooting

Systematic debugging for local dev failures (failed to fetch, CORS, Docker, API errors, LLM flows).

## Checklist

### 1. Stack status
```
docker compose ps
```
Verify all services are running and healthy. Check ports: backend (8000), frontend (WEB_HOST_PORT), postgres (5432).

### 2. Log inspection
```
docker compose logs backend --tail 50
docker compose logs frontend --tail 50
```
Also check `logs/backend.log` when `ENV=local`.

### 3. CORS / preflight verification
```
curl -X OPTIONS http://localhost:8000/health \
  -H "Origin: http://localhost:3300" \
  -H "Access-Control-Request-Method: GET" -v
```
Confirm `CORS_ORIGINS` in `.env` includes the frontend URL.

### 4. API smoke test
```
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/diagnosis/interview/start -X POST -H "Content-Type: application/json" -d '{}'
```

### 5. Environment checklist
Verify in `.env`:
- `OPENAI_API_KEY` — set and valid
- `DATABASE_URL` — points to running Postgres
- `CORS_ORIGINS` — includes frontend URL
- `WEB_HOST_PORT` — matches the port frontend is actually on
- `NEXT_PUBLIC_BACKEND_URL` / `NEXT_PUBLIC_API_URL` — point to backend

### 6. LangSmith traces
If LLM flows fail, inspect traces:
```
./scripts/langsmith-env.sh trace list --project "$LANGSMITH_PROJECT" --last-n-minutes 30 --error
```

### 7. Backend tests
```
make test
```

### 8. Common fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `failed to fetch` in browser | CORS or backend down | Check `CORS_ORIGINS`, restart backend |
| Diagnosis/forge no response | Missing `OPENAI_API_KEY` | Set in `.env`, `make down && make up` |
| Postgres won't start | Port 5432 in use | Stop other Postgres or change port |
| Frontend wrong port | `WEB_HOST_PORT` mismatch | Use `make status` for correct URL |

## Rules
- Never add mock fallbacks — fix the real issue
- Feed new discoveries back to this checklist (section 8)

## Input
Describe the error or symptom you're seeing.
