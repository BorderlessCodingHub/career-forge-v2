---
skill_id: rag-eval
title: RAG evaluation
---

Mission: stop shipping on vibes. Today you learn one skill: map a failed golden-set row to a pipeline stage.

## Knowledge

Faithfulness (Ragas) measures how factually consistent the response is with the retrieved context. Split the answer into claims; score is supported claims / total claims, 0 to 1. A fluent answer with a wrong date is unfaithful.

Source: https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/faithfulness/

Context precision (Ragas) measures whether relevant chunks sit at the top of `retrieved_contexts`, not buried under noise. It is a retriever ranking metric, not a writing metric.

Source: https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/context_precision/

```python
from ragas.metrics.collections import Faithfulness

result = await Faithfulness(llm=llm).ascore(
    user_input=question,
    response=answer,
    retrieved_contexts=chunk_texts,
)
```

A golden set is 20–50 real user questions. Each row stores question, reference answer, and optionally the chunk ids that should retrieve. Run the pipeline offline.

Low faithfulness with good chunks points at generation. High faithfulness with a useless answer points at retrieval (wrong chunks).

## Practice

Cover Check. Gold fact is in the PDF. Retrieved chunks do not contain it. The model answers fluently with a plausible date that is not in those chunks. Which stage do you tag first, and which metric do you expect to be the sick one?

## Check

Tag retrieve (or ingest/chunk) first — the fact never entered context. Faithfulness will also look sick because claims are unsupported, but the root is missing context, not a chatty prompt. Fix chunking/retrieval, then re-score. If chunks later contain the fact and the date is still wrong, then tag generate.

## Done when

- You can define faithfulness and context precision in one sentence each
- You can describe a golden-set workflow (question, reference, retrieved context, score)
- You can map one failed row to a pipeline stage

## Primary source

Read Ragas Faithfulness first (claims vs context). Then Context Precision (ranking of chunks).

https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/faithfulness/

https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/context_precision/

If a step is unclear, ask a follow-up. The teacher can unpack any line before you move on.
