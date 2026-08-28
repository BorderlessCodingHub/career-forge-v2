---
skill_id: rag-embeddings
title: Embeddings fundamentals
---

Mission: decide what "near" means before trusting an embedding ranking.

## Knowledge

An embedding is a dense vector: a learned position for an input, not a compressed copy of its words. Bag-of-words represents which terms occur; a dense embedding can place different words near one another when the model learned that they are used with similar meaning.

Think of Harry Beck's tube map. The printed coordinates are deliberately distorted, but the useful relationships survive: which stations connect and which are near on the network. An embedding model also defines a map. A similarity metric is the ruler used on that map.

![A tube map showing how one embedding model places text by learned meaning](/learn/rag-embeddings-tube-map.svg)

The picture is only a mental model. Real embeddings can have thousands of dimensions, and "near" reflects the model's training objective rather than a universal definition of meaning.

Three common failures follow from forgetting the map and ruler:

- Mixed maps: documents embedded with one model are compared with a query embedded by another. Coordinates from different learned spaces are not comparable.
- Wrong ruler: the index uses a metric that does not match the model card or applies normalization inconsistently.
- Silent map replacement: a model or dimension change is deployed without re-embedding the stored corpus. A model migration is an index migration, with compute, storage, and rollout cost.

The OpenAI model card makes the operating contract concrete:

- `text-embedding-3-small` defaults to 1536 dimensions; `text-embedding-3-large` defaults to 3072 and trades more storage and compute for higher benchmark quality.
- OpenAI embeddings are normalized to length 1. Cosine similarity and Euclidean distance therefore produce the same ranking, and a dot product is a fast cosine calculation.
- The v3 models accept a shorter `dimensions` value when storage or latency matters.
- Query and document vectors must come from the same model and dimension setting.

OpenAI guide: https://developers.openai.com/api/docs/guides/embeddings

> **Operational rule.**
> One index means one embedding map and one metric contract. Changing either requires an explicit migration, not a config-only deploy.

A final trap is treating any transformer output as a sentence embedding. Vanilla BERT's `[CLS]` token was not trained to make sentence-level cosine distance useful. Sentence-BERT (SBERT) adds sentence-pair training and pooling so semantically similar sentences can be compared efficiently. The vector extraction recipe is part of the model contract.

## Practice

Do not read Check yet. For each case, choose dense retrieval, bag-of-words/BM25, or a hybrid, and write one sentence explaining what must remain near.

### Case A — FAQ paraphrase

Your corpus says "How to reset a forgotten password." A learner asks "I cannot remember my login secret." The important words barely overlap.

### Case B — rare error code

Your incident runbook contains `ERR_AUTH_1047`. An operator searches for that exact code among many authentication pages. Only one page contains the code.

For either case, imagine replacing the embedding model next week. Write down what must be rebuilt before old document vectors can be ranked against new query vectors.

## Check

Case A key: dense retrieval should help because the model can place "forgotten password" near "cannot remember my login secret" despite low lexical overlap. Validate that behavior on a small labelled query set rather than assuming every model learned the relation.

Case B key: lexical retrieval should be strong because exact rare-token matching is the signal. A hybrid can preserve that exact match while still adding semantic candidates. Dense-only retrieval can dilute opaque identifiers.

Here is a two-pair cosine check using unit vectors:

- A = `[1.00, 0.00]`
- B = `[0.80, 0.60]`
- C = `[0.20, 0.98]` rounded
- cosine(A, B) = 0.80
- cosine(A, C) = 0.20
- Therefore pair A–B ranks above pair A–C. The order, not a universal score threshold, is the retrieval decision.

```quiz
Which vectors can be compared as positions on one embedding map?
- A) Documents and queries produced by the same model and dimension setting
- B) Documents from a BERT [CLS] output and queries from an unrelated SBERT model
- C) Any vectors that happen to contain the same number of floats
correct: A
why: Equal length is not enough. Both sides must use the same learned space and extraction contract.
```

```quiz
What must happen when a production index changes to a different embedding model?
- A) Re-embed the corpus and rebuild the index before comparing new queries
- B) Keep old document vectors and normalize only each new query
- C) Rename the index because coordinates transfer between embedding maps
correct: A
why: A different model defines a different coordinate system, so stored documents and incoming queries must be migrated together.
```

## Done when

- You can distinguish a dense semantic vector from a bag-of-words representation.
- You keep documents and queries on the same embedding map.
- You choose the similarity metric from the model card and can rank the two cosine pairs above.
- You include corpus re-embedding and index rebuild cost in a model-change plan.

## Primary source

Read Vicki Boykis, *What are embeddings?*, for the engineering and historical foundations behind learned vector representations:

http://vickiboykis.com/what_are_embeddings/index.html

If a step is unclear, ask a follow-up. The teacher can unpack any line before you move on.
