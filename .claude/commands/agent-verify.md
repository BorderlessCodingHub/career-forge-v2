# Gate C — Agent Verify

Run structural and runtime verification before merge.

## Steps

1. Run `make agent-verify`
2. The script checks:
   - Project directory structure compliance
   - API `/health` endpoint responds (if stack is running)
   - PostgreSQL connection (if stack is running)
3. Report verdict: **VERIFIED** or **FAILED**

## If FAILED

- Read the error output
- Fix the identified issues (structure, API, DB)
- Re-run `make agent-verify`

## Extending

To add checks for new behavior, edit `scripts/agent-verify.sh`:
- Add structural checks (file existence, module layout)
- Add API endpoint tests (curl assertions)
- Add DB schema checks (table existence, column validation)

## Notes

- Gate C runs AFTER Gates A+B in the triple QA flow
- Can be run standalone anytime to verify project health
- Exit 0 + `"status": "VERIFIED"` = pass
