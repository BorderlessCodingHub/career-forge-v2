# Yuri spot-check (CAR-18)

**Scope (grill lock):** 4 × `*__mid` golden cases (one per goal) **+** must-have lists. No mandatory UI pass.

**Pedro scoring:** 2026-08-05 — all 16 **PASS** (live forge + scorecards). See [RUBRIC.md](./RUBRIC.md) appendix.

## Cases to review

| Goal | Fixture | Pedro PASS? | Yuri ack |
|------|---------|-------------|---------|
| rag-engineer | `data/golden_cases/rag-engineer__mid.json` | **PASS** (2026-08-05) | _pending_ |
| agent-engineer | `data/golden_cases/agent-engineer__mid.json` | **PASS** (2026-08-05) | _pending_ |
| llm-evals | `data/golden_cases/llm-evals__mid.json` | **PASS** (2026-08-05) | _pending_ |
| fine-tuning | `data/golden_cases/fine-tuning__mid.json` | **PASS** (2026-08-05) | _pending_ |

## Must-have lists

| Goal | Doc | JSON | Yuri ack |
|------|-----|------|----------|
| rag-engineer | [must-haves/rag-engineer.md](../must-haves/rag-engineer.md) | `data/must-haves/rag-engineer.json` | _pending_ |
| agent-engineer | [must-haves/agent-engineer.md](../must-haves/agent-engineer.md) | `data/must-haves/agent-engineer.json` | _pending_ |
| llm-evals | [must-haves/llm-evals.md](../must-haves/llm-evals.md) | `data/must-haves/llm-evals.json` | _pending_ |
| fine-tuning | [must-haves/fine-tuning.md](../must-haves/fine-tuning.md) | `data/must-haves/fine-tuning.json` | _pending_ |

## Checklist for Yuri

1. Pedro scorecard A–E looks fair for each mid case (`snapshot.scorecard` in the JSON).
2. Must-have ids still match the job-signal intent (silence baseline 2026-08-04).
3. Reply here or on Linear CAR-18 with date + ack (or requested edits).

## Record

| Date | Reviewer | Outcome | Notes |
|------|----------|---------|-------|
| 2026-08-05 | Pedro | Scorecards filled 16/16 PASS | Live forge snapshots; awaiting Yuri |
| | Yuri | | |
