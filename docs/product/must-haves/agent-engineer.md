# Must-haves — `agent-engineer`

**Goal:** Agent Engineering (MCP, Tool Use, Failure Modes)  
**Status:** frozen — silence baseline 2026-08-04 (Pedro); Yuri spot-check → CAR-18  
**Corpus:** 30 sources (target 25–40) · sampled 2026-07

## Must-have nodes (10)

| # | Proposed id | Title | Why (1 line) | Freq in corpus |
|---|-------------|-------|--------------|----------------|
| 1 | `agent-tool-use` | Tool & function calling | Core of every agent posting; ReAct / tools before frameworks | 29/30 |
| 2 | `agent-mcp` | Model Context Protocol | Fastest-rising companion skill across frameworks (~18–24% of agent postings) | 22/30 |
| 3 | `agent-orchestration` | Stateful orchestration (LangGraph) | LangGraph / graph runtimes dominate production agent reqs | 26/30 |
| 4 | `agent-planning` | Planning & routing | Controllers, conditional edges, multi-node graphs | 24/30 |
| 5 | `agent-memory` | Agent memory & context | Memory / context engineering called out as quality differentiator | 20/30 |
| 6 | `agent-multi-agent` | Multi-agent coordination | Explicit multi-agent / crew roles in platform & consulting postings | 18/30 |
| 7 | `agent-failure-modes` | Failure modes & recovery | Retries, timeouts, partial failure, tool errors — production bar | 21/30 |
| 8 | `agent-observability` | Agent tracing & eval | LangSmith / Langfuse / Arize; “read traces like an SRE” | 25/30 |
| 9 | `agent-guardrails` | Guardrails & permissions | Auth, rate limits, tool permission, safety for enterprise | 17/30 |
| 10 | `agent-ship` | Ship production agents | Durable execution, HITL/checkpoints, deploy, CI — not toy demos | 27/30 |

## Sources

### Direct job postings

1. Planera — Senior AI Agent Engineer (LangGraph + MCP) — https://jobs.ashbyhq.com/planera/d68c8a09-a11d-409e-85ca-5d434caf3fc8
2. Thorit — Agentic Engineer — https://jobs.ashbyhq.com/thorit/13fc5ea3-8d7e-4be1-b41b-437aec00d4a1
3. ClickUp — Senior AI Engineer, Multi-Agent Frameworks — https://jobs.ashbyhq.com/clickup/b8ff5d05-8158-42bb-8d87-296848a0e99f
4. LangChain — Senior Backend, LangSmith Deployments — https://jobs.ashbyhq.com/langchain/cb61f821-d8c4-4ec5-940d-3fd83be63a5f
5. LangChain — Senior Backend, AI Observability & Evals (LangSmith) — https://jobs.ashbyhq.com/LangChain/f07c1416-f126-4925-8606-5dd7c5a90f6f
6. Siemens — AI Retrieval & Agent Platform Engineer — https://jobs.siemens.com/en_US/externaljobs/JobDetail/512534
7. Anthropic (via StudySmarter) — Software Engineer, Model Context Protocol — https://talents.studysmarter.co.uk/companies/anthropic/software-engineer-model-context-protocol-2845004/
8. SOUM — AI / GenAI Solutions Engineer (agentic + RAG) — https://jobs.lever.co/soum/838e99ac-69e7-40a2-a9b2-fb098194c1a8
9. Parallel Wireless — Generative AI Platform Engineer — https://jobs.lever.co/parallelwireless/233858ab-104d-42fe-8b5b-f9d86aa8f5a4
10. Egen — Senior AI Engineer (agentic workflows) — https://jobs.lever.co/egen/1b870652-5768-45e9-b55b-4420e6402314
11. StaffXpert — AI/ML Engineer (LangGraph + vector) — https://www.iitjobs.com/job/aiml-engineer-milpitas-ca-usa-354385
12. Deliveroo — GenAI Platform Engineer — https://builtin.com/job/software-engineer-genai-platform/10257403
13. Braintrust — Software Engineer, Backend — https://jobs.ashbyhq.com/Braintrust/9728653e-49b9-4f5c-b6cd-7dbc6a6d5fcc
14. Braintrust — Open Source Engineer, Python — https://jobs.ashbyhq.com/Braintrust/ba4d6676-f65c-42c9-84ee-285f2da15e0d
15. Collective.work — LLMOps & Observability Engineer — https://www.collective.work/jobs/en/llmops-and-observability-engineer-gpyr
16. Pydantic — Evals & Continuous Learning Engineer — https://pydantic.dev/jobs/evals-continuous-learning-engineer
17. Crunchyroll — LLM Engineer III — https://boards.greenhouse.io/crunchyroll/jobs/7014513
18. Oowlish — Senior LLM Engineer — https://jobs.lever.co/oowlish/765cab63-09c4-4963-a095-720abb851e19

### Market synthesis

19. Presenc AI — AI Agent Engineer Career Guide 2026 — https://presenc.ai/research/agent-engineer-career-guide-2026
20. Agentic Engineering Jobs — Frameworks job market 2026 — https://agentic-engineering-jobs.com/ai-agent-frameworks-job-market-2026
21. DEV Community — Top AI Agent Frameworks 2026 — https://dev.to/thedailyagent/top-7-ai-agent-frameworks-for-developers-in-2026-3o63
22. AI Learning Guides — Production AI Agents with LangGraph and MCP — https://ailearningguides.com/production-ai-agents-langgraph-mcp-2026-build-guide/
23. Adnan Masood — State of agent frameworks 2026 — https://medium.com/@adnanmasood/state-of-agent-frameworks-choosing-the-right-runtime-for-enterprise-ai-execution-cc69653ffb10
24. Daniel Lee — AI Engineer job 2026 (agents + context) — https://www.linkedin.com/posts/danleedata_how-to-land-an-ai-engineer-job-in-2026-activity-7411406010751537152-v0I9
25. Second Talent — LLMOps Engineer 2026 — https://www.secondtalent.com/occupations/llmops-engineer/
26. Kore1 — Hire RAG Engineers 2026 (agentic retrieval context) — https://www.kore1.com/hire-rag-engineers-2026/
27. Langfuse — Evaluating agents via LLM-as-a-Judge — https://heidloff.net/article/langfuse-evaluations/
28. Greenhouse newsroom — Greenhouse MCP launch (enterprise tool governance) — https://www.greenhouse.com/newsroom/greenhouse-launches-mcp-giving-hiring-teams-a-governed-way-to-connect-ai-tools-to-greenhouse
29. Pinecone — Search & Retrieval Infrastructure (agentic systems) — https://www.pinecone.io/careers/499ce77a-7ed0-462e-9efb-3e7dad6cd5ad/
30. Careerium — Staff MLOps / LLMOps — https://careerium.unaux.com/job/staff-mlops-engineer-llmops

## Notes for F2 (CAR-17)

- **Catalog overlap:** `agent-tool-use`, `agent-mcp`, `agent-planning`, `agent-memory`, `agent-failure-modes`, `agent-observability`, `agent-ship` map to CAR-5 seeds.
- **Gaps:** `agent-orchestration` (LangGraph/HITL), `agent-multi-agent`, `agent-guardrails` — propose catalog nodes in F2.
- Prefer skill outcomes over vendor lock-in; MCP + one orchestration runtime is enough for lean forge.
- No wiring in this PR.
