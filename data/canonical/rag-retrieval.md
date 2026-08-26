---
skill_id: rag-retrieval
title: Vector retrieval
---

Mission: turn chunks into hits a generator can use. Today you learn one skill: tell empty-index apart from low-relevance hits.

## Knowledge

Build: embed each chunk, upsert `(id, vector, metadata)` into an index whose dimension matches the embedding model.

Query: embed the question with the same model, ask for top-k nearest neighbors, read text plus metadata back.

Pinecone query takes a `vector` (or a stored `id`) and requires `topK`. Matches come back most-similar first. Set `includeMetadata` true when the LLM needs source text. Leave vector values out unless you are debugging — they inflate payload and latency.

Source: https://docs.pinecone.io/reference/api/2026-04/data-plane/query

```python
matches = index.query(
    vector=query_embedding,
    top_k=8,
    include_metadata=True,
)
```

Empty result set: wrong namespace, empty index, or a filter that matches nothing.

Low-relevance hits with decent scores: different embedding models on ingest vs query, chunking cut the fact, or the question is too vague to land near any chunk.

## Practice

Cover Check. A query returns eight hits. Scores look fine. None of the chunk texts contain the gold fact, which you know is in the PDF. Name the failure class, then one fix. Do not say "the model is bad".

## Check

Failure class: bad chunking (or ingest), not an empty index. The index returned neighbors; they were the wrong neighbors.

One fix: re-chunk that source by section, re-upsert the same ids so stale vectors disappear, then re-query. Also confirm ingest and query used the same embedding model before you touch k.

Other levers after that: inspect chunk text not just ids; if a verbatim keyword would have found it, dense-only is the gap (hybrid is a later skill); raise k then rerank rather than stuffing k=50 into the prompt.

## Done when

- You can narrate upsert then query without skipping metadata
- You can name empty-index versus bad-chunking versus bad-query as distinct failures
- You can propose one change (re-chunk, same model, filter, or k) for a low-relevance trace

## Primary source

Read the Pinecone query API: `vector`, required `topK`, `includeMetadata`.

https://docs.pinecone.io/reference/api/2026-04/data-plane/query

If a step is unclear, ask a follow-up. The teacher can unpack any line before you move on.
