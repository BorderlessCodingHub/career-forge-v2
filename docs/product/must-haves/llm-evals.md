# Must-haves — `llm-evals`

**Goal:** LLM Evaluation & Observability (LLMOps)  
**Status:** frozen — silence baseline 2026-08-04 (Pedro); Yuri spot-check → CAR-18  
**Corpus:** 28 sources (target 25–40) · sampled 2026-07

## Must-have nodes (10)

| # | Proposed id | Title | Why (1 line) | Freq in corpus |
|---|-------------|-------|--------------|----------------|
| 1 | `evals-metrics` | Offline quality metrics | Task metrics, faithfulness, relevance — baseline of every eval role | 27/28 |
| 2 | `evals-llm-judge` | LLM-as-a-judge | Default scalable grader when ground truth is scarce | 25/28 |
| 3 | `evals-datasets` | Eval datasets & curation | Golden sets, versioning, access control, trace→dataset loops | 24/28 |
| 4 | `evals-regression` | Regression & CI gates | Release gates / CI eval suites required for production LLMOps | 22/28 |
| 5 | `evals-tracing` | Distributed LLM tracing | Spans for prompts, retrieval, tools — OpenTelemetry / Langfuse / LangSmith | 26/28 |
| 6 | `evals-online` | Online / production evals | Sampled live scoring, quality alerts, continuous learning | 20/28 |
| 7 | `evals-prompt-versioning` | Prompt & model versioning | Prompt libraries, experiment compare, rollback — platform postings | 19/28 |
| 8 | `evals-cost-latency` | Cost & latency observability | Token economics, p95 latency, cost attribution | 21/28 |
| 9 | `evals-guardrails-safety` | Safety & guardrail scoring | PII, toxicity, refusal, moderation checks in ops roles | 16/28 |
| 10 | `evals-llmops` | LLMOps platform practice | Gateway, tooling choice (Langfuse/LangSmith/Braintrust), runbooks | 23/28 |

## Sources

### Direct job postings

1. Collective.work — LLMOps & Observability Engineer — https://www.collective.work/jobs/en/llmops-and-observability-engineer-gpyr
2. LangChain — Senior Backend, AI Observability & Evals (LangSmith) — https://jobs.ashbyhq.com/LangChain/f07c1416-f126-4925-8606-5dd7c5a90f6f
3. LangChain — EM, AI Observability & Evals Platform — https://jobs.ashbyhq.com/LangChain/e1263bfe-b638-4019-b4d5-0aacca93b2b3
4. LangChain — Senior Backend, LangSmith Deployments — https://jobs.ashbyhq.com/langchain/cb61f821-d8c4-4ec5-940d-3fd83be63a5f
5. Braintrust — Software Engineer, Backend — https://jobs.ashbyhq.com/Braintrust/9728653e-49b9-4f5c-b6cd-7dbc6a6d5fcc
6. Braintrust — Open Source Engineer, Python — https://jobs.ashbyhq.com/Braintrust/ba4d6676-f65c-42c9-84ee-285f2da15e0d
7. Pydantic — Evals & Continuous Learning Engineer — https://pydantic.dev/jobs/evals-continuous-learning-engineer
8. Careerium — Staff MLOps Engineer, LLMOps — https://careerium.unaux.com/job/staff-mlops-engineer-llmops
9. Planera — Senior AI Agent Engineer (eval + observability stack) — https://jobs.ashbyhq.com/planera/d68c8a09-a11d-409e-85ca-5d434caf3fc8
10. Thorit — Agentic Engineer (observability fluency) — https://jobs.ashbyhq.com/thorit/13fc5ea3-8d7e-4be1-b41b-437aec00d4a1
11. ClickUp — Senior AI Engineer (evaluation frameworks) — https://jobs.ashbyhq.com/clickup/b8ff5d05-8158-42bb-8d87-296848a0e99f
12. Parallel Wireless — Generative AI Platform Engineer (offline/online eval) — https://jobs.lever.co/parallelwireless/233858ab-104d-42fe-8b5b-f9d86aa8f5a4
13. Crunchyroll — LLM Engineer III (monitor hallucination/latency/cost) — https://boards.greenhouse.io/crunchyroll/jobs/7014513
14. Deliveroo — GenAI Platform (evals + guardrails) — https://builtin.com/job/software-engineer-genai-platform/10257403
15. Siemens — AI Retrieval & Agent Platform (observability stack) — https://jobs.siemens.com/en_US/externaljobs/JobDetail/512534
16. APPIT — RAG & Retrieval Systems Engineer (eval frameworks) — https://www.appitsoftware.com/careers/rag-retrieval-systems-engineer-hyderabad

### Market synthesis

17. Second Talent — LLMOps Engineer skills 2026 — https://www.secondtalent.com/occupations/llmops-engineer/
18. DevOpsSchool — Senior LLMOps Engineer role blueprint — https://www.devopsschool.com/blog/senior-llmops-engineer-role-blueprint-responsibilities-skills-kpis-and-career-path/
19. Langfuse docs — LLM-as-a-Judge — https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
20. Heidloff — Evaluating agents via LLM-as-a-Judge in Langfuse — https://heidloff.net/article/langfuse-evaluations/
21. Ankur Somani — LLM-as-Judge vs observability — https://www.linkedin.com/pulse/llm-judge-enough-why-observability-becoming-real-ankur-somani-cjtqf
22. Kore1 — Hire RAG Engineers 2026 (eval harness as hire bar) — https://www.kore1.com/hire-rag-engineers-2026/
23. AY Automate — RAG frameworks 2026 (RAGAS as default eval bolt-on) — https://www.ayautomate.com/blog/best-rag-frameworks
24. Presenc AI — Agent Engineer guide (eval engineering premium) — https://presenc.ai/research/agent-engineer-career-guide-2026
25. Agentic Engineering Jobs — frameworks + LangSmith pairing — https://agentic-engineering-jobs.com/ai-agent-frameworks-job-market-2026
26. Daniel Lee — AI Engineer 2026 (human loop / AI judge) — https://www.linkedin.com/posts/danleedata_how-to-land-an-ai-engineer-job-in-2026-activity-7411406010751537152-v0I9
27. Vikas Singh — RAGAS for RAG evaluation — https://www.linkedin.com/posts/itvika_ragas-rag-genai-activity-7480232673454477312-Wf3k
28. Cornellius Y. — RAG evaluation / LLM-as-Judge — https://www.linkedin.com/posts/cornellius-yudha-wijaya_rag-is-good-evaluation-makes-it-better-activity-7287906714819993601-SbZF

## Notes for F2 (CAR-17)

- **Catalog overlap:** all 7 CAR-5 seed ids (`evals-metrics` … `evals-llmops`) kept.
- **Gaps:** `evals-prompt-versioning`, `evals-cost-latency`, `evals-guardrails-safety`.
- Soft-gate / golden harness in F2 should treat offline metrics + tracing + regression as non-negotiable for this track.
- No wiring in this PR.
