# Cost gate report template (CAR-7)

> Fill via `./scripts/cost-gate.sh` — do not edit by hand for the official gate.
> Output lands in `docs/reports/YYYY-MM-DD-cost-gate.md`.

## Required sections (generator)

1. **Verdict** — GO / CONDITIONAL / NO-GO vs R$500 hard · R$700 ceiling
2. **FX** — fixed `COST_FX_USD_BRL` (default 5.50)
3. **Method** — synthetic `_cost.synthetic_gate=true` + token usage × OpenAI list prices
4. **Assumptions** — pilot students × forges/user × diagnosis/other runs
5. **Tables** — mean + P95 by `graph_name` and by `goal_id`
6. **Recommended env** — `COST_P95_BRL_PER_RUN=…`
7. **Ledger** — per-run BRL + duration

## Commands

```bash
./scripts/cost-gate.sh                  # 24 forges + samples (default)
./scripts/cost-gate.sh --forges 20
make cost-gate
```
