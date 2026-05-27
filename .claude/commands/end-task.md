# End Task — Post-merge workflow

Mandatory after every merge to main.

## Steps

1. **Verify merge landed**:
   ```
   git log --oneline -5
   ```
   Confirm the merge commit is on main.

2. **Update Linear issue status**:
   - Use Linear MCP `save_issue` to set status → **Done**
   - This is MANUAL — there is no GitHub↔Linear automation

3. **Update docs/STATUS.md**:
   - Mark the issue as complete in the parity matrix
   - Update the "last merge" entry

4. **Update docs/ROADMAP.md**:
   - Check off the completed item in the sprint checklist

5. **Self-critique drift check**:
   - Did the merge introduce duplicate modules?
   - Does the structure still comply with REPO-STRUCTURE.md?
   - Any orphan files left behind?
   - Any legacy paths still referenced?

6. **Report to user**:
   - Merge summary (commit hash, branch, issue)
   - Gate verdicts from the triple QA
   - Any blockers or follow-up items

## Input
Provide the HAC-XX issue identifier that was just merged.
