# Diagnosis UI — agent notes

**Parent spec:** [DIAGNOSIS-INTERVIEW.md](../../../../docs/product/DIAGNOSIS-INTERVIEW.md)  
**Decisions:** [ADR-001](../../../../docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md)

## Role of this folder

Onboarding screens: goal picker (screen 1), adaptive interview (screen 2), editable diagnosis (screen 3).

## Screen 2 rules

- Fetch questions from `POST /diagnosis/interview/start` and `.../turn`
- Render `InterviewQuestion[]` — topic pill, question, placeholder from `example_of_answer`
- Sidebar `mapping_progress` from API — not hardcoded `DIAG_MAP_LABELS` in prod
- Do not embed question logic or rubric in TS constants

## Screen 1

- Real user input only (no pre-filled motivation)
- `CvDropzone` → send PDF on interview start (not sessionStorage-only in prod)

## Cursor rule

`.cursor/rules/diagnosis-interview.mdc` applies to all files here.
