.PHONY: smoke agent-verify up down status test

# Stub smoke — extend when apps/web + apps/api + docker-compose land (HAC-5)
smoke:
	@echo "== Career Forge smoke (bootstrap) =="
	@test -f AGENTS.md
	@test -f docs/STATUS.md
	@test -f docs/ROADMAP.md
	@test -f .cursor/rules/end-task-workflow.mdc
	@test -f .cursor/rules/ui-product-sync.mdc
	@test -f claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md
	@test -f claude-design-docs/UX-FLOW.md
	@test -f claude-design-docs/SCREEN-INTENT.md
	@test -f claude-design-docs/references/roadmap-sh-vertical-ai-tutor.png
	@test -f claude-design-docs/BORDERLESS-THEMING.md
	@test -f claude-design-docs/references/borderless-code-breakers-dashboard.png
	@test -f claude-design-docs/references/borderless-logo-brand.png
	@test -f claude-design-docs/prototype/Career\ Forge.html
	@bash scripts/agent-verify.sh
	@echo "SMOKE OK (harness + stub verify)"

agent-verify:
	@bash scripts/agent-verify.sh

up:
	@echo "TODO HAC-5: docker compose up"

down:
	@echo "TODO HAC-5: docker compose down"

status:
	@echo "Harness bootstrap active — apps not yet scaffolded"

test:
	@echo "TODO: pytest + pnpm test when monorepo exists"
