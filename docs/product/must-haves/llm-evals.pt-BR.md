# Must-haves — `llm-evals`

> Versão em inglês (fonte canônica): [llm-evals.md](./llm-evals.md)

**Goal:** LLM Evaluation & Observability (LLMOps) (avaliação e observabilidade de LLM)  
**Status:** congelado — silence baseline 2026-08-04 (Pedro); spot-check Yuri → CAR-18  
**Corpus:** 28 fontes (meta 25–40) · amostrado em 2026-07

## Nós must-have (10)

| # | id proposto | Título | Por quê (1 linha) | Freq no corpus |
|---|-------------|--------|-------------------|----------------|
| 1 | `evals-metrics` | Métricas de qualidade offline | Métricas de tarefa, faithfulness, relevância — base de toda vaga de eval | 27/28 |
| 2 | `evals-llm-judge` | LLM-as-a-judge | Avaliador escalável padrão quando falta ground truth | 25/28 |
| 3 | `evals-datasets` | Datasets de eval & curadoria | Golden sets, versionamento, controle de acesso, loops trace→dataset | 24/28 |
| 4 | `evals-regression` | Regressão & gates de CI | Release gates / suites de eval em CI exigidos para LLMOps em produção | 22/28 |
| 5 | `evals-tracing` | Tracing distribuído de LLM | Spans para prompts, retrieval, tools — OpenTelemetry / Langfuse / LangSmith | 26/28 |
| 6 | `evals-online` | Evals online / em produção | Scoring amostrado ao vivo, alertas de qualidade, continuous learning | 20/28 |
| 7 | `evals-prompt-versioning` | Versionamento de prompt & modelo | Bibliotecas de prompt, comparação de experimentos, rollback — vagas de plataforma | 19/28 |
| 8 | `evals-cost-latency` | Observabilidade de custo & latência | Economia de tokens, latência p95, atribuição de custo | 21/28 |
| 9 | `evals-guardrails-safety` | Scoring de segurança & guardrails | PII, toxicidade, refusal, moderação em vagas de ops | 16/28 |
| 10 | `evals-llmops` | Prática de plataforma LLMOps | Gateway, escolha de ferramentas (Langfuse/LangSmith/Braintrust), runbooks | 23/28 |

## Fontes

### Vagas diretas

1. Collective.work — LLMOps & Observability Engineer — https://www.collective.work/jobs/en/llmops-and-observability-engineer-gpyr
2. LangChain — Senior Backend, AI Observability & Evals (LangSmith) — https://jobs.ashbyhq.com/LangChain/f07c1416-f126-4925-8606-5dd7c5a90f6f
3. LangChain — EM, AI Observability & Evals Platform — https://jobs.ashbyhq.com/LangChain/e1263bfe-b638-4019-b4d5-0aacca93b2b3
4. LangChain — Senior Backend, LangSmith Deployments — https://jobs.ashbyhq.com/langchain/cb61f821-d8c4-4ec5-940d-3fd83be63a5f
5. Braintrust — Software Engineer, Backend — https://jobs.ashbyhq.com/Braintrust/9728653e-49b9-4f5c-b6cd-7dbc6a6d5fcc
6. Braintrust — Open Source Engineer, Python — https://jobs.ashbyhq.com/Braintrust/ba4d6676-f65c-42c9-84ee-285f2da15e0d
7. Pydantic — Evals & Continuous Learning Engineer — https://pydantic.dev/jobs/evals-continuous-learning-engineer
8. Careerium — Staff MLOps Engineer, LLMOps — https://careerium.unaux.com/job/staff-mlops-engineer-llmops
9. Planera — Senior AI Agent Engineer (stack de eval + observabilidade) — https://jobs.ashbyhq.com/planera/d68c8a09-a11d-409e-85ca-5d434caf3fc8
10. Thorit — Agentic Engineer (fluência em observabilidade) — https://jobs.ashbyhq.com/thorit/13fc5ea3-8d7e-4be1-b41b-437aec00d4a1
11. ClickUp — Senior AI Engineer (frameworks de avaliação) — https://jobs.ashbyhq.com/clickup/b8ff5d05-8158-42bb-8d87-296848a0e99f
12. Parallel Wireless — Generative AI Platform Engineer (eval offline/online) — https://jobs.lever.co/parallelwireless/233858ab-104d-42fe-8b5b-f9d86aa8f5a4
13. Crunchyroll — LLM Engineer III (monitorar alucinação/latência/custo) — https://boards.greenhouse.io/crunchyroll/jobs/7014513
14. Deliveroo — GenAI Platform (evals + guardrails) — https://builtin.com/job/software-engineer-genai-platform/10257403
15. Siemens — AI Retrieval & Agent Platform (stack de observabilidade) — https://jobs.siemens.com/en_US/externaljobs/JobDetail/512534
16. APPIT — RAG & Retrieval Systems Engineer (frameworks de eval) — https://www.appitsoftware.com/careers/rag-retrieval-systems-engineer-hyderabad

### Síntese de mercado

17. Second Talent — LLMOps Engineer skills 2026 — https://www.secondtalent.com/occupations/llmops-engineer/
18. DevOpsSchool — Senior LLMOps Engineer role blueprint — https://www.devopsschool.com/blog/senior-llmops-engineer-role-blueprint-responsibilities-skills-kpis-and-career-path/
19. Langfuse docs — LLM-as-a-Judge — https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
20. Heidloff — Evaluating agents via LLM-as-a-Judge in Langfuse — https://heidloff.net/article/langfuse-evaluations/
21. Ankur Somani — LLM-as-Judge vs observability — https://www.linkedin.com/pulse/llm-judge-enough-why-observability-becoming-real-ankur-somani-cjtqf
22. Kore1 — Hire RAG Engineers 2026 (eval harness como critério de contratação) — https://www.kore1.com/hire-rag-engineers-2026/
23. AY Automate — RAG frameworks 2026 (RAGAS como eval padrão acoplável) — https://www.ayautomate.com/blog/best-rag-frameworks
24. Presenc AI — Agent Engineer guide (prêmio de eval engineering) — https://presenc.ai/research/agent-engineer-career-guide-2026
25. Agentic Engineering Jobs — frameworks + pareamento com LangSmith — https://agentic-engineering-jobs.com/ai-agent-frameworks-job-market-2026
26. Daniel Lee — AI Engineer 2026 (human loop / AI judge) — https://www.linkedin.com/posts/danleedata_how-to-land-an-ai-engineer-job-in-2026-activity-7411406010751537152-v0I9
27. Vikas Singh — RAGAS for RAG evaluation — https://www.linkedin.com/posts/itvika_ragas-rag-genai-activity-7480232673454477312-Wf3k
28. Cornellius Y. — RAG evaluation / LLM-as-Judge — https://www.linkedin.com/posts/cornellius-yudha-wijaya_rag-is-good-evaluation-makes-it-better-activity-7287906714819993601-SbZF

## Notas para a F2 (CAR-17)

- **Overlap com catálogo:** todos os 7 ids de seed da CAR-5 (`evals-metrics` … `evals-llmops`) mantidos.
- **Lacunas:** `evals-prompt-versioning`, `evals-cost-latency`, `evals-guardrails-safety`.
- O soft-gate / golden harness na F2 deve tratar métricas offline + tracing + regressão como inegociáveis nesta trilha.
- Sem wiring neste PR.
