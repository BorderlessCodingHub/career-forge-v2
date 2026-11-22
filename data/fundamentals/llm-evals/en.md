---
goal_id: llm-evals
locale: en
---

An eval checks a behavior you can fail. Observability is the record of that check on a real run.

## Score a behavior, then keep the trace

A score without a named behavior is a vibe. Write the behavior first: the answer must cite a passage, the tool call must match the schema, the refusal must hold. The eval runs that check on a set of examples and records which ones failed.

A trace is the run itself: the prompt, the retrieved passages, the tool calls, the model output, and the score. When a later request gets worse, the trace is what shows whether the prompt, the retrieval, or the judge moved. A dashboard that only shows an average hides the example that failed.
