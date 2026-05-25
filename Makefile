.PHONY: smoke agent-verify up down status test stack-smoke seed help

COMPOSE ?= docker compose

help:
	@echo "Career Forge — make targets:"
	@echo "  make up            Start docker stack (postgres + backend + frontend)"
	@echo "  make down          Stop docker stack"
	@echo "  make status        Show compose status + URLs"
	@echo "  make test          Backend pytest (apps/backend)"
	@echo "  make smoke         Full harness + stack health"
	@echo "  make seed           Seed skill catalog + demo Ana (requires DATABASE_URL)"
	@echo "  make stack-smoke   Docker stack health only"

# Full smoke — harness + monorepo + stack health (starts docker if needed)
smoke:
	@echo "== Career Forge smoke =="
	@test -f AGENTS.md
	@test -f docs/STATUS.md
	@test -f docs/ROADMAP.md
	@test -f docs/engineering/REPO-STRUCTURE.md
	@test -f apps/frontend/package.json
	@test -f apps/backend/requirements.txt
	@test -f apps/backend/src/career_forge/main.py
	@test -f docker-compose.yml
	@test -f .env.example
	@bash scripts/agent-verify.sh
	@bash scripts/smoke-stack.sh
	@echo "SMOKE OK"

agent-verify:
	@bash scripts/agent-verify.sh

stack-smoke:
	@bash scripts/smoke-stack.sh

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

status:
	@$(COMPOSE) ps
	@echo ""
	@echo "Frontend: http://localhost:$${WEB_HOST_PORT:-3000}"
	@echo "Backend:  http://localhost:8000/docs"
	@echo "Health:   http://localhost:8000/health"

test:
	@echo "== Backend tests =="
	@cd apps/backend && PYTHONPATH=src python -m pytest -q 2>/dev/null || (pip install -q -r requirements.txt pytest httpx && PYTHONPATH=src python -m pytest -q)

seed:
	@echo "== Seed catalog + demo Ana =="
	@cd apps/backend && PYTHONPATH=src python -m scripts.seed --demo-ana
