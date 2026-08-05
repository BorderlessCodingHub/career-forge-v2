# Golden cases (CAR-18)

Sixteen fixtures: `{goal_id}__{persona}.json`  
Personas: `early` · `mid` · `staff` · `soft-gated-weak`  
Goals: `rag-engineer` · `agent-engineer` · `llm-evals` · `fine-tuning`

| Doc | Path |
|-----|------|
| Pedro runbook | [docs/product/golden-cases/PEDRO-RUNBOOK.md](../../docs/product/golden-cases/PEDRO-RUNBOOK.md) |
| Rubric | [docs/product/golden-cases/RUBRIC.md](../../docs/product/golden-cases/RUBRIC.md) |
| Cutoff | [docs/product/golden-cases/SOFT-GATE-CUTOFF.md](../../docs/product/golden-cases/SOFT-GATE-CUTOFF.md) |
| Yuri spot-check | [docs/product/golden-cases/YURI-SPOTCHECK.md](../../docs/product/golden-cases/YURI-SPOTCHECK.md) |
| Template | [`_TEMPLATE.json`](./_TEMPLATE.json) |

```bash
make golden-check          # CI / local deterministic
make golden-run CASE=rag-engineer__mid
make golden-run ALL=1      # refresh coverage on all 16
make golden-run ALL=1 LIVE=1   # live forge (needs OPENAI_API_KEY)
```

Regenerate skeletons (overwrites JSON):

```bash
cd apps/backend && PYTHONPATH=src python -m scripts.generate_golden_cases
```
