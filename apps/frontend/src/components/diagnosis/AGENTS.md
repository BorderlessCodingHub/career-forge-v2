# Diagnosis UI — agent notes

**Parent spec:** [DIAGNOSIS-INTERVIEW.md](../../../../docs/product/DIAGNOSIS-INTERVIEW.md)  
**Decisions:** [ADR-001](../../../../docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md)

## Role of this folder

Onboarding screens: goal picker (screen 1), adaptive interview (screen 2), editable diagnosis (screen 3).

## Screen 2 rules

- Fetch questions via `useDiagnosisInterview` (`lib/hooks/useDiagnosisInterview.ts`) → `POST /diagnosis/interview/start` and `.../turn`
- `DiagnosticPills` is presentation-only; intake/build helpers live in `lib/diagnosis-interview.ts`
- Sidebar recap: `OnboardingRecapSidebar`; mapping list: `MappingDimensionList`
- Render `InterviewQuestion[]` — topic pill, question, placeholder from `example_of_answer`
- Sidebar `mapping_progress` from API — skeleton from `buildSkeletonMappingProgress()` only while loading
- Do not embed question logic or rubric in TS constants

## Screen 1

- Real user input only (no pre-filled motivation)
- `CvDropzone` accepts PDF only (matches backend `CvAttachment.mime_type`)
- Shared years-xp labels: `lib/years-xp.ts`

## Cursor rule

`.cursor/rules/diagnosis-interview.mdc` applies to all files here.
