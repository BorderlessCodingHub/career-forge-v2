# Career Forge API — AI JSON contracts (HAC-7)

Pydantic models and LangGraph `TypedDict` state types. **No LangGraph graphs yet** — schemas only.

## Layout

```
app/schemas/     # Central exports (import from app.schemas)
fixtures/        # Example JSON for tests and replay fallback
tests/           # pytest schema validation
```

## Schemas

| Model | Role |
|-------|------|
| `DiagnosisResponse` | Onboarding diagnosis output |
| `RoadmapForgeEvent` | SSE union (discriminated by `type`) |
| `SkillGraphState` | LangGraph forge accumulator |
| `GraphPatch` | LLM node update proposal |
| `ValidationResponse` | Mastery interview result |
| `PlanUpdateResponse` | Adaptive mission banner |

Supporting: `SkillNode`, `UserSkillNode`, `UserSkillNodePartial`, `NodePatch`, `DiagnosisProfile`, enums `SkillStatus`, `Priority`, `ValidationStatus`.

## Run tests

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## TypeScript mirror

`apps/web/src/types/contracts.ts` — keep in sync when schemas change.
