# Session Smoke Test

Run before ending any session that touched code or infrastructure.

## When to run

After modifying any of:
- `apps/` (frontend or backend code)
- `scripts/`
- `Makefile`
- `docker-compose*.yml`
- `.env*` files
- Infrastructure or deploy config

## Steps

1. Run `make smoke`
   - If make smoke is not available: run `make test` as fallback
   - If no make targets available: `curl -fsS http://localhost:8000/health`

2. Check output for failures

3. If failures:
   - Read error output
   - Fix issues
   - Re-run smoke

4. Report: **GREEN** (all pass) or **RED** (failures with details)

## What smoke checks

- Docker stack health (`docker compose ps`)
- Backend `/health` endpoint
- Backend test suite
- Project structure validation
