---
goal_id: rag-engineer
locale: en
---

A production RAG system retrieves passages first, then asks the model to answer from those passages.

## Retrieve before the model writes

A model that only remembers training will answer from whatever it saw when it was trained. That memory goes stale, and it has no way to point at the document the learner is supposed to trust. Retrieval-augmented generation adds a content store in front of the write. The question hits the store first. The model then writes with those passages in the prompt, not from memory alone.

The store can be a closed collection — policies, runbooks, tickets, a product corpus — or an open one such as the public web. The contract is the same either way: the answer is only as current as the passages that were retrieved, and a reader should be able to see which passages were used.

Two failures show up before any ranking trick matters. The first is answering with no source. The second is answering from a source that no longer matches the world. Retrieval is the beat that looks the fact up before the sentence is written.

## Chunks the retriever can find

The retriever does not search the corpus as one blob. It searches chunks: pieces small enough to rank, large enough to still say something. A chunk that splits a definition from its exception will retrieve the definition and drop the exception. A chunk that pastes three unrelated topics together will match the query on one topic and drag the other two into the prompt.

A useful chunk keeps one claim, the condition that limits it, and enough neighboring words that the claim still makes sense alone. Overlap between neighboring chunks is there so a sentence that sits on a boundary is not the only copy. The embedding, when one is used, has to be the same model and the same dimension for the query and for every stored chunk. Mixing maps makes "near" meaningless.

Lexical search still earns a place when the query names an identifier, an error code, or a product term the embedding was never trained to treat as special. Many production systems run both and fuse the lists. The fusion rule is part of the system, not a detail to invent at read time.

## Answer from the passages

The prompt that reaches the model has three jobs. It says to answer from the retrieved passages. It includes those passages. It includes the question. If the passages do not contain the answer, the model should say so. A fluent paragraph that ignores the passages is the failure retrieval was added to prevent.

Citations belong next to the claim they support. A link to the whole corpus is not a citation. The reader, and any later check, needs the passage. When two passages disagree, the answer should show the disagreement instead of averaging them into a third fact that neither source stated.

Generation settings do not repair a bad retrieval. A lower temperature makes the wording steadier. It does not put a missing passage back into the prompt. When the answer is wrong, look at what was retrieved before you look at how the model was sampled.

## Watch the retrieval loop

Marina Danilevsky, at IBM Research, walks through the same loop: a model that answers from training memory, then the same question after a content store is consulted first. The video is the short version of why the lookup happens before the write.

https://www.youtube.com/watch?v=T-D1OfcDW1M

## Know when the answer is unsupported

Treat a run as unsupported when the retrieved passages do not state the claim, when they state a different claim, or when the store that should have held the fact returned nothing. Logging the question, the chunk ids, and the answer is the minimum record. Without it, a wrong answer cannot be traced to a bad chunk, a stale index, or a model that ignored the prompt.

Re-embedding is an index migration. Changing the embedding model, its dimension, or the chunking rule means the stored vectors no longer share a map with new queries. Ship that as a rebuild, with a way to compare the old ranking and the new one on questions you already trust.

The guide stays the same for every learner on this Goal. A roadmap built later is a personal path through skills. It does not rewrite this reading.
