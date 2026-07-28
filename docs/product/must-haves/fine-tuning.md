# Must-haves — `fine-tuning`

**Goal:** Fine-Tuning & Alignment (LoRA, DPO, Custom Models)  
**Status:** draft — awaiting Yuri sign-off (silence = baseline)  
**Corpus:** 28 sources (target 25–40) · sampled 2026-07

## Must-have nodes (10)

| # | Proposed id | Title | Why (1 line) | Freq in corpus |
|---|-------------|-------|--------------|----------------|
| 1 | `ft-when-to-tune` | When to fine-tune vs prompt | Decision skill; postings expect pragmatic build-vs-prompt judgment | 18/28 |
| 2 | `ft-data-prep` | Fine-tune data preparation | Curation, chat templates, preference pairs — first bottleneck | 26/28 |
| 3 | `ft-sft` | Supervised fine-tuning (SFT) | Default first stage of post-training stack | 27/28 |
| 4 | `ft-lora` | LoRA / PEFT | Parameter-efficient methods dominate 2026 job reqs | 25/28 |
| 5 | `ft-quantization` | QLoRA & quantization | QLoRA / GPTQ / AWQ for memory-constrained training & serve | 20/28 |
| 6 | `ft-dpo` | Preference optimization (DPO) | DPO/ORPO/KTO replacing full RLHF as default preference path | 22/28 |
| 7 | `ft-alignment` | Alignment & safety post-training | RLHF/RLAIF/refusal/behavior targets in senior roles | 19/28 |
| 8 | `ft-eval` | Fine-tune evaluation | Held-out, benchmarks, LLM-judge, A/B before ship | 24/28 |
| 9 | `ft-distributed` | Distributed training | FSDP / DeepSpeed / multi-GPU for serious post-training roles | 17/28 |
| 10 | `ft-serve` | Serve adapted models | Merge adapters, vLLM/TGI, inference cost/latency | 21/28 |

## Sources

### Direct job postings

1. Baseten — Machine Learning Engineer, Fine Tuning — https://builtin.com/job/machine-learning-engineer-fine-tuning/4573762
2. Character.AI — Principal Research Engineer, Post-Training — https://jobs.ashbyhq.com/character/cab23a8b-97ba-4b20-a8e3-f7d9a61e13f4
3. NewsBreak — ML Engineer, LLM Post-Training — https://builtin.com/job/machine-learning-engineer-llm-post-training/9693189
4. Distyl AI — Applied AI Researcher, Post-Training — https://builtin.com/job/applied-ai-researcher-post-training/7415515
5. Kindo — Senior Applied AI/ML Scientist (post-training) — https://builtin.com/job/senior-applied-ai-ml-scientist/8629269
6. SuperDial — Staff Machine Learning Engineer (SFT / LoRA) — https://www.workway.dev/job/superdial-staff-machine-learning-engineer-db67c48c-0c73-4ba9-a900-fd7ade8a32ff
7. Deliveroo — Software Engineer, GenAI Platform (SFT/DPO/LoRA) — https://builtin.com/job/software-engineer-genai-platform/10257403
8. Parallel Wireless — Local LLM & Generative AI Platform Engineer — https://jobs.lever.co/parallelwireless/233858ab-104d-42fe-8b5b-f9d86aa8f5a4
9. Egen — Senior AI Engineer (embedding / LLM fine-tuning) — https://jobs.lever.co/egen/1b870652-5768-45e9-b55b-4420e6402314
10. Crunchyroll — LLM Engineer III — https://boards.greenhouse.io/crunchyroll/jobs/7014513
11. Careerium — Staff MLOps Engineer, LLMOps — https://careerium.unaux.com/job/staff-mlops-engineer-llmops
12. Collective.work — LLMOps & Observability Engineer — https://www.collective.work/jobs/en/llmops-and-observability-engineer-gpyr
13. Pydantic — Evals & Continuous Learning Engineer — https://pydantic.dev/jobs/evals-continuous-learning-engineer
14. LangChain — LangSmith Observability & Evals — https://jobs.ashbyhq.com/LangChain/f07c1416-f126-4925-8606-5dd7c5a90f6f
15. Planera — Senior AI Agent Engineer — https://jobs.ashbyhq.com/planera/d68c8a09-a11d-409e-85ca-5d434caf3fc8
16. Oowlish — Senior LLM Engineer (RAG & Bedrock) — https://jobs.lever.co/oowlish/765cab63-09c4-4963-a095-720abb851e19

### Market synthesis

17. Second Talent — Fine-Tuning Engineer 2026 — https://www.secondtalent.com/occupations/fine-tuning-engineer/
18. JobDescription.org — Fine-tuning Engineer JD — https://jobdescription.org/jobs/artificial-intelligence/fine-tuning-engineer
19. AI Market Pulse — LLM fine-tuning skills — https://theaimarketpulse.com/insights/llm-fine-tuning-skills/
20. FutureAGI — LLM Fine-Tuning Techniques 2026 (LoRA, QLoRA, DPO) — https://futureagi.com/blog/llm-fine-tuning-techniques-i-ii/
21. DEV Community — Fine-tune with LoRA/QLoRA 2026 guide — https://dev.to/jangwook_kim_e31e7291ad98/fine-tune-llms-with-lora-and-qlora-2026-guide-33lf
22. NOVASOLUTIONS — Mistral fine-tuning (LoRA/QLoRA/DPO stack) — https://novasolutions.technology/ai-development/services/llm/mistral-fine-tuning.html
23. Second Talent — LLMOps Engineer 2026 — https://www.secondtalent.com/occupations/llmops-engineer/
24. DevOpsSchool — Senior LLMOps blueprint — https://www.devopsschool.com/blog/senior-llmops-engineer-role-blueprint-responsibilities-skills-kpis-and-career-path/
25. Kore1 — Hire RAG Engineers 2026 (when not to fine-tune) — https://www.kore1.com/hire-rag-engineers-2026/
26. Daniel Lee — AI Engineer 2026 — https://www.linkedin.com/posts/danleedata_how-to-land-an-ai-engineer-job-in-2026-activity-7411406010751537152-v0I9
27. Presenc AI — Agent Engineer guide (model adaptation context) — https://presenc.ai/research/agent-engineer-career-guide-2026
28. AI Learning Guides — Production agents 2026 (adaptation vs tools) — https://ailearningguides.com/production-ai-agents-langgraph-mcp-2026-build-guide/

## Notes for F2 (CAR-17)

- **Catalog overlap:** `ft-data-prep`, `ft-sft`, `ft-lora`, `ft-eval`, `ft-dpo`, `ft-serve`, `ft-alignment` map to CAR-5 seeds.
- **Gaps:** `ft-when-to-tune`, `ft-quantization`, `ft-distributed`.
- Lean forge should emphasize SFT → LoRA → DPO → eval → serve; full RLHF as optional depth, not a separate must-have.
- No wiring in this PR.
