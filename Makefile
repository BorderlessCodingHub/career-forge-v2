.PHONY: smoke agent-verify up down status test stack-smoke seed cost-gate cost-report must-have-coverage golden-check golden-run premium-landings help

COMPOSE ?= docker compose

help:
	@echo "Career Forge — make targets:"
	@echo "  make up            Start docker stack (postgres + backend + frontend)"
	@echo "  make down          Stop docker stack"
	@echo "  make status        Show compose status + URLs"
	@echo "  make test          Backend pytest (apps/backend)"
	@echo "  make smoke         Full harness + stack health"
	@echo "  make seed           Seed skill catalog + demo Ana (requires DATABASE_URL)"
	@echo "  make cost-gate     CAR-7 synthetic cost gate + Yuri report"
	@echo "  make cost-report   CAR-43 production cost rollup (graph_runs)"
	@echo "  make must-have-coverage  CAR-17 must-have ≥70% smoke harness"
	@echo "  make golden-check  CAR-18 deterministic golden suite"
	@echo "  make golden-run    CAR-18 Pedro helper (CASE=… / ALL=1 / LIVE=1)"
	@echo "  make stack-smoke   Docker stack health only"
	@echo "  make premium-landings  Rebuild /welcome/premium-a and /welcome/premium-b HTML"

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

premium-landings:
	@bash scripts/build-premium-landings.sh

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

status:
	@$(COMPOSE) ps
	@echo ""
	@echo "Frontend: http://localhost:$${WEB_HOST_PORT:-3300}/career-forge"
	@echo "Backend:  http://localhost:8000/docs"
	@echo "Health:   http://localhost:8000/health"

test:
	@bash scripts/test-backend.sh

seed:
	@echo "== Seed catalog + demo Ana =="
	@cd apps/backend && PYTHONPATH=src python -m scripts.seed --demo-ana

cost-gate:
	@bash scripts/cost-gate.sh

cost-report:
	@bash scripts/cost-report.sh

must-have-coverage:
	@bash scripts/must-have-coverage.sh

golden-check:
	@bash scripts/golden-check.sh

# Examples:
#   make golden-run CASE=rag-engineer__mid
#   make golden-run ALL=1
#   make golden-run ALL=1 LIVE=1
golden-run:
	@args=""; \
	if [ -n "$${CASE:-}" ]; then args="$$args --case $${CASE}"; fi; \
	if [ "$${ALL:-}" = "1" ]; then args="$$args --all"; fi; \
	if [ "$${LIVE:-}" = "1" ]; then args="$$args --live"; fi; \
	bash scripts/golden-run.sh $$args
