# Must-haves — `rag-engineer`

**Goal:** Production RAG & Advanced Retrieval  
**Status:** draft — awaiting Yuri sign-off (silence = baseline)  
**Corpus:** 32 sources (target 25–40) · sampled 2026-07

## Must-have nodes (10)

| # | Proposed id | Title | Why (1 line) | Freq in corpus |
|---|-------------|-------|--------------|----------------|
| 1 | `rag-embeddings` | Embeddings fundamentals | Almost every RAG posting requires embedding model choice + similarity | 30/32 |
| 2 | `rag-chunking` | Chunking & ingestion | Parsing/chunking/metadata called out as the failure point of production RAG | 28/32 |
| 3 | `rag-retrieval` | Vector retrieval | Vector DB / ANN / top-k search is table stakes | 31/32 |
| 4 | `rag-hybrid-search` | Hybrid search (dense + lexical) | Pure vector-only called outdated; BM25 + dense + filters dominate 2026 reqs | 24/32 |
| 5 | `rag-rerank` | Reranking | Cross-encoder / Cohere / ColBERT rerank appears with hybrid search | 22/32 |
| 6 | `rag-grounding` | Grounding & citations | Source attribution / groundedness / permission-aware retrieval | 20/32 |
| 7 | `rag-eval` | Retrieval evaluation | Recall@k, faithfulness, RAGAS/TruLens/Phoenix — “ship without eval” rejected | 26/32 |
| 8 | `rag-orchestration` | RAG orchestration frameworks | LangChain / LlamaIndex / custom orchestrator named in most mid+ roles | 23/32 |
| 9 | `rag-production` | Production RAG ops | Index freshness, deletion, latency/cost, deploy on cloud | 25/32 |
| 10 | `rag-latency-cost` | Latency & cost budgets | Explicit SLO / token / infra cost tradeoffs in senior postings | 18/32 |

## Sources

### Direct job postings

1. Siemens — AI Retrieval & Agent Platform Engineer — https://jobs.siemens.com/en_US/externaljobs/JobDetail/512534
2. APPIT Software — RAG & Retrieval Systems Engineer — https://www.appitsoftware.com/careers/rag-retrieval-systems-engineer-hyderabad
3. Oowlish — Senior LLM Engineer (RAG & AWS Bedrock) — https://jobs.lever.co/oowlish/765cab63-09c4-4963-a095-720abb851e19
4. Crunchyroll — LLM Engineer III — https://boards.greenhouse.io/crunchyroll/jobs/7014513
5. Egen — Senior AI Engineer (RAG / Vertex) — https://jobs.lever.co/egen/1b870652-5768-45e9-b55b-4420e6402314
6. Parallel Wireless — Local LLM & Generative AI Platform Engineer — https://jobs.lever.co/parallelwireless/233858ab-104d-42fe-8b5b-f9d86aa8f5a4
7. SOUM — AI / GenAI Solutions Engineer — https://jobs.lever.co/soum/838e99ac-69e7-40a2-a9b2-fb098194c1a8
8. Pinecone — Senior/Staff SWE, Search & Retrieval Infrastructure — https://www.pinecone.io/careers/499ce77a-7ed0-462e-9efb-3e7dad6cd5ad/
9. StaffXpert / IITJobs — AI/ML Engineer (RAG, Qdrant/Pinecone/Weaviate) — https://www.iitjobs.com/job/aiml-engineer-milpitas-ca-usa-354385
10. Planera — Senior AI Agent Engineer (RAG + MCP) — https://jobs.ashbyhq.com/planera/d68c8a09-a11d-409e-85ca-5d434caf3fc8

### Adjacent AI/platform postings (retrieval skills required)

11. ClickUp — Senior AI Engineer, Multi-Agent Frameworks — https://jobs.ashbyhq.com/clickup/b8ff5d05-8158-42bb-8d87-296848a0e99f
12. Thorit — Agentic Engineer — https://jobs.ashbyhq.com/thorit/13fc5ea3-8d7e-4be1-b41b-437aec00d4a1
13. Deliveroo — Software Engineer, GenAI Platform — https://builtin.com/job/software-engineer-genai-platform/10257403
14. Collective.work — LLMOps & Observability Engineer — https://www.collective.work/jobs/en/llmops-and-observability-engineer-gpyr
15. Careerium — Staff MLOps Engineer, LLMOps — https://careerium.unaux.com/job/staff-mlops-engineer-llmops
16. Pydantic — Evals & Continuous Learning Engineer — https://pydantic.dev/jobs/evals-continuous-learning-engineer
17. LangChain — Senior Backend, LangSmith Observability & Evals — https://jobs.ashbyhq.com/LangChain/f07c1416-f126-4925-8606-5dd7c5a90f6f
18. LangChain — Senior Backend, LangSmith Deployments — https://jobs.ashbyhq.com/langchain/cb61f821-d8c4-4ec5-940d-3fd83be63a5f

### Market synthesis (aggregated posting signals)

19. Kore1 — How to Hire RAG Engineers in 2026 — https://www.kore1.com/hire-rag-engineers-2026/
20. AY Automate — Best RAG Frameworks 2026 — https://www.ayautomate.com/blog/best-rag-frameworks
21. Zen van Riel — Vector Database Engineer Jobs — https://zenvanriel.com/job/vector-database-engineer-jobs/
22. Daniel Lee — How to Land an AI Engineer job in 2026 — https://www.linkedin.com/posts/danleedata_how-to-land-an-ai-engineer-job-in-2026-activity-7411406010751537152-v0I9
23. Data Science Collective — Pinecone vs Weaviate vs Qdrant vs Milvus — https://medium.com/data-science-collective/pinecone-vs-weaviate-vs-qdrant-vs-milvus-66d5bfbcc460
24. Second Talent — LLMOps Engineer skills 2026 — https://www.secondtalent.com/occupations/llmops-engineer/
25. DevOpsSchool — Senior LLMOps Engineer role blueprint — https://www.devopsschool.com/blog/senior-llmops-engineer-role-blueprint-responsibilities-skills-kpis-and-career-path/
26. Langfuse docs — LLM-as-a-Judge (RAG eval practice) — https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
27. Agentic Engineering Jobs — AI agent frameworks job market 2026 — https://agentic-engineering-jobs.com/ai-agent-frameworks-job-market-2026
28. Presenc AI — Agent Engineer Career Guide 2026 — https://presenc.ai/research/agent-engineer-career-guide-2026
29. AI Learning Guides — Production agents LangGraph + MCP 2026 — https://ailearningguides.com/production-ai-agents-langgraph-mcp-2026-build-guide/
30. FutureAGI — LLM fine-tuning techniques (RAG vs tune tradeoff context) — https://futureagi.com/blog/llm-fine-tuning-techniques-i-ii/
31. JobDescription.org — Fine-tuning Engineer JD patterns — https://jobdescription.org/jobs/artificial-intelligence/fine-tuning-engineer
32. Second Talent — Fine-Tuning Engineer 2026 — https://www.secondtalent.com/occupations/fine-tuning-engineer/

## Notes for F2 (CAR-17)

- **Catalog overlap:** all 7 CAR-5 seed ids (`rag-embeddings` … `rag-production`) kept as must-haves.
- **Gaps to add later:** `rag-hybrid-search`, `rag-orchestration`, `rag-latency-cost` (not in beginner catalog JSON).
- Lean prune = these 10 + one foundation layer (prereqs), per V2-PLAN F2.10.
- No wiring in this PR.
