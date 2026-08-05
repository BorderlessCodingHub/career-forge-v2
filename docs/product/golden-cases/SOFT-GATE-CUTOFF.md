# Soft-gate cutoff (CAR-18 retune)

| Field | Value |
|-------|-------|
| **Previous (CAR-15 provisional)** | `0.55` |
| **Current default** | `0.50` |
| **Formula** | midpoint(max weak `profile_score`, min early `profile_score`) |
| **Seed inputs** | weak=`0.42`, early=`0.58` → `(0.42+0.58)/2 = 0.50` |
| **Env** | `SOFT_GATE_CUTOFF` (see `.env.example`) |
| **Code** | `career_forge.services.soft_gate.DEFAULT_SOFT_GATE_CUTOFF` |

After Pedro edits hand-seeds, recompute:

```bash
make golden-check
# scripts print recommended_midpoint=…
```

Then update this file + default if the midpoint moves. Keep **one global** cutoff (V2-PLAN F2.5).
