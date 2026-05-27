# Start a Linear issue

Workflow to begin work on a Linear issue.

## Steps

1. **Read context** (in order):
   - CLAUDE.md → docs/ROADMAP.md → docs/SPRINT-BOARD.md → docs/STATUS.md → docs/CHECKPOINT.md

2. **Get issue from Linear** via MCP:
   - Use `get_issue` to fetch acceptance criteria
   - Confirm scope is a single HAC-XX issue

3. **Create branch**:
   ```
   git checkout main && git pull origin main
   git checkout -b HAC-XX-title-slug
   ```
   Use Linear "Copy git branch name" format when available.

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
Provide the Linear issue identifier (e.g., HAC-42) or describe the task.
