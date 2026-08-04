# Must-have id lists — machine-readable (CAR-15 → CAR-17)

Human drafts / freeze SoT: [`docs/product/must-haves/`](../docs/product/must-haves/).

These JSON files list **frozen** must-have ids (10/goal) used by:

- Lean forge prune (CAR-15)
- Forge bias (`must_have_node_ids`) + post-forge inject (CAR-17)
- Coverage harness (`make must-have-coverage`)

| File | Goal |
|------|------|
| `rag-engineer.json` | `rag-engineer` |
| `agent-engineer.json` | `agent-engineer` |
| `llm-evals.json` | `llm-evals` |
| `fine-tuning.json` | `fine-tuning` |

**Freeze:** silence baseline 2026-08-04 (Pedro). Yuri spot-check on CAR-18.
