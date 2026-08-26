---
skill_id: rag-chunking
title: Chunking strategies
---

Mission: retrieval searches chunks, not whole PDFs. Today you learn one skill: pick a split and keep source metadata on every chunk.

## Knowledge

LangChain's RecursiveCharacterTextSplitter is the recommended starting point for generic prose. It tries paragraph breaks, then newlines, then spaces, then characters, so related sentences stay together until they no longer fit `chunk_size`.

`chunk_overlap` copies the tail of one chunk onto the next so a sentence on the cut is not lost. Overlap must stay smaller than size. The 1000 / 200 numbers in the docs are a demo, not a law.

Source: https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter

Use that fixed-size recursion when the dump is messy. Use heading- or section-aware splits when the corpus already has structure (docs site, markdown handbook, API reference).

Attach `source` and `section` on every chunk before embed. Hits return that metadata so you can cite and debug. If it is dropped at ingest, retrieval still "works" and you cannot tell why a miss happened.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents(
    [text],
    metadatas=[{"source": path, "section": heading}],
)
```

## Practice

Cover Check. For a messy policy PDF with no headings, which split do you start with, and what two metadata keys must survive into the index?

For an API reference where each page is one endpoint, what changes?

## Check

Messy PDF: recursive fixed-size first (try ~400–800 tokens and ~10–20% overlap, then measure recall@k). Metadata keys: `source` and `section`.

API reference: split on headings so each chunk is one endpoint. Same metadata keys. The change is the separator, not dropping metadata.

## Done when

- You can say when fixed-size wins versus heading-aware splits
- You can justify size and overlap for one real corpus, not a blog default
- You can show source/section still present on a retrieved hit

## Primary source

Read the LangChain recursive splitter page — parameters `chunk_size` and `chunk_overlap`.

https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter

If a step is unclear, ask a follow-up. The teacher can unpack any line before you move on.
