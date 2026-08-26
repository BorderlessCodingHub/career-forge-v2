---
skill_id: rag-production
title: Production RAG
---

Mission: a notebook is not a service. Today you learn one skill: name latency, cost, and freshness as separate knobs, then say what a trace must show.

## Knowledge

Serve one endpoint: query in, answer plus citations out. Cap p95 on embed-query + retrieve + generate. Levers: smaller embedding model, `top_k` you actually use, no vector values on the query payload, cache the query embedding for identical questions, stream tokens so time-to-first-token is not the full generation.

Cost follows prompt tokens (context you stuffed) and vector-db read units. Freshness is a third axis: a cheap, fast index that is a week behind a changing corpus is still wrong.

LangSmith records a request as a tree. Mark the retriever `run_type="retriever"` and return Document-shaped objects (`page_content`, `type="Document"`, `metadata`) so the UI shows chunk text. Wrap generation too. Then a bad answer is inspectable: empty retrieve versus unfaithful generate.

Source: https://docs.langchain.com/langsmith/log-retriever-trace

Upsert by stable chunk id when a source changes. Delete ids for files that left the corpus. Key any query cache on a `corpus_version` so a re-index does not serve yesterday. Invalidate that cache when you change embedding model — old vectors are not comparable.

## Practice

Cover Check. p95 is fine, answers cite last month's policy, and you cannot tell whether retrieve or generate failed. What two production concerns are you mixing, and what two spans must the next trace contain?

## Check

You mixed latency (fine) with freshness (stale policy). The missing observability is the retriever span plus the generation span in one tree.

Fix freshness with upsert/delete and a cache key tied to corpus version. Fix visibility with a retriever run that returns documents, then a generation run. Do not turn the latency knob to solve staleness.

## Done when

- You can name latency, cost, and freshness as separate production concerns
- You can describe a retriever span plus a generation span in one trace
- You can outline upsert/delete plus cache keys tied to corpus version

## Primary source

Walk the LangSmith RAG observability tutorial (full pipeline, not only the LLM call). Then the retriever-trace page for `run_type="retriever"`.

https://docs.langchain.com/langsmith/observability-llm-tutorial

https://docs.langchain.com/langsmith/log-retriever-trace

If a step is unclear, ask a follow-up. The teacher can unpack any line before you move on.
