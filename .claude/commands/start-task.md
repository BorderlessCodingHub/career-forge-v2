# Start a Linear issue

Workflow to begin work on a Linear issue (Career Forge V2 · `CAR-XX`).

## Steps

1. **Read context** (in order):
   - CLAUDE.md / AGENTS.md → docs/V2-PLAN.md → docs/ROADMAP.md → docs/STATUS.md → docs/CHECKPOINT.md

2. **Get issue from Linear** via MCP:
   - Use `get_issue` to fetch acceptance criteria
   - Confirm scope is a single CAR-XX issue
   - Set state → **In Progress**

3. **Create branch**:
   ```
   git checkout main && git pull origin main
   git checkout -b CAR-XX-title-slug
   ```
   Strip any `username/` prefix from Linear's suggested branch name.

4. **Classify issue**:
   - **P** (parallel) — independent, can run with others
   - **S** (sequential) — depends on prior issue output
   - **B** (blocker) — blocks entire batch

5. **If 2+ P issues** with satisfied deps exist, report to user for parallel dispatch.

6. **Read domain-specific docs** before coding:
   - AI/LangGraph → docs/engineering/EXECUTION-FLOW.md + AI-EXECUTION.md
   - Frontend → claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md
   - Diagnosis → docs/decisions/ADR-001 + docs/product/DIAGNOSIS-INTERVIEW.md

7. **Start implementation** — target 200–500 LOC.

## Input
Provide the Linear issue identifier (e.g., CAR-5) or describe the task.
