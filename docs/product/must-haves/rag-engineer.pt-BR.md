# Must-haves — `rag-engineer`

> Versão em inglês (fonte canônica): [rag-engineer.md](./rag-engineer.md)

**Goal:** Production RAG & Advanced Retrieval (RAG em produção e retrieval avançado)  
**Status:** congelado — silence baseline 2026-08-04 (Pedro); spot-check Yuri → CAR-18  
**Corpus:** 32 fontes (meta 25–40) · amostrado em 2026-07

## Nós must-have (10)

| # | id proposto | Título | Por quê (1 linha) | Freq no corpus |
|---|-------------|--------|-------------------|----------------|
| 1 | `rag-embeddings` | Fundamentos de embeddings | Quase toda vaga de RAG exige escolha de modelo de embedding + similaridade | 30/32 |
| 2 | `rag-chunking` | Chunking & ingestão | Parsing/chunking/metadados apontados como o ponto de falha do RAG em produção | 28/32 |
| 3 | `rag-retrieval` | Retrieval vetorial | Vector DB / ANN / busca top-k é o básico obrigatório | 31/32 |
| 4 | `rag-hybrid-search` | Busca híbrida (denso + lexical) | Só-vetorial visto como ultrapassado; BM25 + denso + filtros dominam os requisitos de 2026 | 24/32 |
| 5 | `rag-rerank` | Reranking | Rerank com cross-encoder / Cohere / ColBERT aparece junto com busca híbrida | 22/32 |
| 6 | `rag-grounding` | Grounding & citações | Atribuição de fonte / groundedness / retrieval consciente de permissões | 20/32 |
| 7 | `rag-eval` | Avaliação de retrieval | Recall@k, faithfulness, RAGAS/TruLens/Phoenix — "subir sem eval" é rejeitado | 26/32 |
| 8 | `rag-orchestration` | Frameworks de orquestração de RAG | LangChain / LlamaIndex / orquestrador próprio citados na maioria das vagas mid+ | 23/32 |
| 9 | `rag-production` | Ops de RAG em produção | Frescor do índice, deleção, latência/custo, deploy em nuvem | 25/32 |
| 10 | `rag-latency-cost` | Orçamentos de latência & custo | Trade-offs explícitos de SLO / tokens / custo de infra em vagas sênior | 18/32 |

## Fontes

### Vagas diretas

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

### Vagas adjacentes de IA/plataforma (exigem skills de retrieval)

11. ClickUp — Senior AI Engineer, Multi-Agent Frameworks — https://jobs.ashbyhq.com/clickup/b8ff5d05-8158-42bb-8d87-296848a0e99f
12. Thorit — Agentic Engineer — https://jobs.ashbyhq.com/thorit/13fc5ea3-8d7e-4be1-b41b-437aec00d4a1
13. Deliveroo — Software Engineer, GenAI Platform — https://builtin.com/job/software-engineer-genai-platform/10257403
14. Collective.work — LLMOps & Observability Engineer — https://www.collective.work/jobs/en/llmops-and-observability-engineer-gpyr
15. Careerium — Staff MLOps Engineer, LLMOps — https://careerium.unaux.com/job/staff-mlops-engineer-llmops
16. Pydantic — Evals & Continuous Learning Engineer — https://pydantic.dev/jobs/evals-continuous-learning-engineer
17. LangChain — Senior Backend, LangSmith Observability & Evals — https://jobs.ashbyhq.com/LangChain/f07c1416-f126-4925-8606-5dd7c5a90f6f
18. LangChain — Senior Backend, LangSmith Deployments — https://jobs.ashbyhq.com/langchain/cb61f821-d8c4-4ec5-940d-3fd83be63a5f

### Síntese de mercado (sinais agregados de vagas)

19. Kore1 — How to Hire RAG Engineers in 2026 — https://www.kore1.com/hire-rag-engineers-2026/
20. AY Automate — Best RAG Frameworks 2026 — https://www.ayautomate.com/blog/best-rag-frameworks
21. Zen van Riel — Vector Database Engineer Jobs — https://zenvanriel.com/job/vector-database-engineer-jobs/
22. Daniel Lee — How to Land an AI Engineer job in 2026 — https://www.linkedin.com/posts/danleedata_how-to-land-an-ai-engineer-job-in-2026-activity-7411406010751537152-v0I9
23. Data Science Collective — Pinecone vs Weaviate vs Qdrant vs Milvus — https://medium.com/data-science-collective/pinecone-vs-weaviate-vs-qdrant-vs-milvus-66d5bfbcc460
24. Second Talent — LLMOps Engineer skills 2026 — https://www.secondtalent.com/occupations/llmops-engineer/
25. DevOpsSchool — Senior LLMOps Engineer role blueprint — https://www.devopsschool.com/blog/senior-llmops-engineer-role-blueprint-responsibilities-skills-kpis-and-career-path/
26. Langfuse docs — LLM-as-a-Judge (prática de eval de RAG) — https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
27. Agentic Engineering Jobs — AI agent frameworks job market 2026 — https://agentic-engineering-jobs.com/ai-agent-frameworks-job-market-2026
28. Presenc AI — Agent Engineer Career Guide 2026 — https://presenc.ai/research/agent-engineer-career-guide-2026
29. AI Learning Guides — Production agents LangGraph + MCP 2026 — https://ailearningguides.com/production-ai-agents-langgraph-mcp-2026-build-guide/
30. FutureAGI — LLM fine-tuning techniques (contexto do trade-off RAG vs tune) — https://futureagi.com/blog/llm-fine-tuning-techniques-i-ii/
31. JobDescription.org — Fine-tuning Engineer JD patterns — https://jobdescription.org/jobs/artificial-intelligence/fine-tuning-engineer
32. Second Talent — Fine-Tuning Engineer 2026 — https://www.secondtalent.com/occupations/fine-tuning-engineer/

## Notas para a F2 (CAR-17)

- **Overlap com catálogo:** todos os 7 ids de seed da CAR-5 (`rag-embeddings` … `rag-production`) mantidos como must-haves.
- **Lacunas a adicionar depois:** `rag-hybrid-search`, `rag-orchestration`, `rag-latency-cost` (não estão no JSON do catálogo beginner).
- Lean prune = esses 10 + uma camada de foundation (prereqs), conforme V2-PLAN F2.10.
- Sem wiring neste PR.
