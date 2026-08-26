---
skill_id: rag-embeddings
title: Embeddings fundamentals
---

Mission: ship retrieval that ranks by meaning, not keywords. Today you learn one skill: read a cosine ranking on a three-string toy set.

## Knowledge

An embedding is a dense vector of floats. Nearby vectors mean nearby meaning.

OpenAI maps a string to a fixed-length vector. Their embeddings are normalized to length 1, so cosine similarity equals a dot product and ranks the same as Euclidean distance.

Source: https://developers.openai.com/api/docs/guides/embeddings

```python
import numpy as np

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

`text-embedding-3-small` defaults to 1536 dimensions. `text-embedding-3-large` defaults to 3072, scores higher on MTEB, and costs more to store. You can pass `dimensions` (for example 1024) to shorten a v3 vector. Query and documents must use the same model.

## Practice

Do not look at Check yet. From memory, rank these two pairs: which cosine should be higher?

- "refund policy" with "how do I get my money back"
- "refund policy" with "office wifi password"

Then name one size-versus-quality trade-off you would pick for a first index.

## Check

The money-back pair should rank higher. Rank order matters more than the raw number (often the close pair sits above 0.7; the wifi pair sits clearly lower).

A first index: start with `text-embedding-3-small`. Move to large only if a golden set shows recall@k stuck after chunking and retrieval are already sane.

## Done when

- You can say dense semantic vector without mixing it up with bag-of-words
- You can name one size-versus-quality trade-off (small vs large, or dimensions)
- You can interpret two cosine scores on a three-sentence toy set

## Primary source

Read the OpenAI embeddings guide, especially cosine ranking and the small vs large table.

https://developers.openai.com/api/docs/guides/embeddings

If a step is unclear, ask a follow-up. The teacher can unpack any line before you move on.
