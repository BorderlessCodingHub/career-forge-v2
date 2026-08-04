# Must-have nodes — F1 draft / F2 freeze (CAR-8 → CAR-17)

> Versão em português: [README.pt-BR.md](./README.pt-BR.md)

Lean forge acceptance in F2 measures **≥70% post-forge coverage** of these must-haves (per goal), via human QA — not job RAG in the product ([V2-PLAN.md](../../V2-PLAN.md)).

| Goal | Doc | Nodes | Corpus size |
|------|-----|-------|-------------|
| `rag-engineer` | [rag-engineer.md](./rag-engineer.md) | 10 | 32 |
| `agent-engineer` | [agent-engineer.md](./agent-engineer.md) | 10 | 30 |
| `llm-evals` | [llm-evals.md](./llm-evals.md) | 10 | 28 |
| `fine-tuning` | [fine-tuning.md](./fine-tuning.md) | 10 | 28 |

## Freeze status (CAR-17)

**Silence baseline — frozen 2026-08-04 by Pedro** (grill CAR-17). Yuri one-round review was invited under CAR-8; no blocking edits received. Spot-check deferred to **CAR-18** golden QA.

Machine-readable SoT: [`data/must-haves/*.json`](../../../data/must-haves/) (full 10 ids/goal). Catalog gap seeds shipped in CAR-17.

## Sign-off protocol

1. **Draft** (CAR-8) — Pedro authors from a lean job corpus (~25–40 sources/goal).
2. **One round** — Yuri reviews; silence = **baseline freeze** for F2 harness (CAR-17 / CAR-18).
3. **Wiring** — lean prune + forge bias/inject + ≥70% coverage harness (**CAR-17**). Formal golden acceptance = **CAR-18**.

## Sampling notes

- Sampled **2026-07** from public ATS boards (Lever, Greenhouse, Ashby, company careers) plus hiring guides that synthesize posting requirements.
- Freq = approximate share of corpus sources that mention the skill (or a clear synonym). Not a statistical market study.
- English-first titles; BASE/PSP lean fit (job-market signals, not exhaustive IR research).
