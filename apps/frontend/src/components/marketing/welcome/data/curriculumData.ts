export interface PillarData {
  id: 'rag' | 'finetuner' | 'evals' | 'opsllm';
  title: string;
  badge: string;
  subtitle: string;
  description: string;
  gradient: string;
  accentColor: string;
  borderColor: string;
  iconName: string;
  skills: string[];
  techStack: { name: string; logo: string }[];
  capstoneProject: {
    title: string;
    description: string;
    deliverables: string[];
  };
  codeSnippet: {
    filename: string;
    language: string;
    code: string;
    output: string;
  };
  architectureFlow: {
    step: string;
    title: string;
    description: string;
  }[];
}

export const PILLARS: PillarData[] = [
  {
    id: 'rag',
    title: 'RAG Engineering',
    badge: 'Retrieval & Context Orchestration',
    subtitle: 'Master Hybrid Search, GraphRAG, & Agentic Query Systems',
    description: 'Build enterprise-grade Retrieval-Augmented Generation architectures that handle millions of vector embeddings, hybrid dense/sparse indexing, reranking, and dynamic context compression with zero hallucination leaks.',
    gradient: 'from-amber-500/20 via-orange-500/10 to-transparent',
    accentColor: 'text-orange-400',
    borderColor: 'border-orange-500/30',
    iconName: 'Database',
    skills: [
      'Hybrid Dense & Sparse Retrieval (BM25 + Cohere Rerank v3)',
      'Agentic RAG & Hierarchical GraphRAG with Neo4j',
      'Context Compression, Chunking Strategies & Parent-Child Indexing',
      'Semantic Caching with Redis & Qdrant for 10x Latency Drop',
      'Multi-modal Vector Embeddings & PDF/OCR Pipeline Processing'
    ],
    techStack: [
      { name: 'Qdrant', logo: '⚡' },
      { name: 'LlamaIndex', logo: '🦙' },
      { name: 'LangChain', logo: '🦜' },
      { name: 'Pinecone', logo: '🌲' },
      { name: 'Cohere', logo: '🔮' },
      { name: 'Neo4j', logo: '🕸️' }
    ],
    capstoneProject: {
      title: 'Production GraphRAG Engine over 50,000 SEC 10-K Filings',
      description: 'Architect an end-to-end agentic retrieval pipeline with reciprocal rank fusion (RRF) and dynamic self-corrective retrieval loops achieving 98.4% context precision.',
      deliverables: ['Self-hosted Qdrant cluster', 'RAGAS benchmark score >0.92', 'Sub-300ms p95 latency API']
    },
    codeSnippet: {
      filename: 'agentic_graph_rag.py',
      language: 'python',
      code: `from careerforge.rag import HybridRetriever, CohereReranker, KnowledgeGraph
from qdrant_client import QdrantClient

# Step 1: Initialize Hybrid Vector + Knowledge Graph Index
client = QdrantClient(url="https://qdrant.cluster.internal:6334")
retriever = HybridRetriever(
    vector_store=client,
    sparse_encoder="splade-v2",
    dense_model="text-embedding-3-large",
    rrf_k=60
)

# Step 2: Query Decomposition & Graph Expansion
async def query_financial_rag(user_query: str):
    expanded_nodes = await KnowledgeGraph.expand_entities(user_query)
    dense_docs = await retriever.search(user_query, top_k=50)
    
    # Rerank using Cohere v3 with metadata filtering
    reranked_context = CohereReranker.filter(
        query=user_query,
        documents=dense_docs,
        graph_entities=expanded_nodes,
        top_n=5
    )
    return reranked_context.synthesize_with_guardrails()`,
      output: '✓ Query processed in 184ms | Precision@5: 0.96 | Tokens compressed: 64%'
    },
    architectureFlow: [
      { step: '01', title: 'Query Rewriting', description: 'HyDE (Hypothetical Document Embeddings) & Multi-Query expansion' },
      { step: '02', title: 'Hybrid Retrieval', description: 'Parallel BM25 sparse + HNSW dense vector search with metadata filters' },
      { step: '03', title: 'Reciprocal Rank Fusion', description: 'Score merging with RRF algorithm & Cohere v3 reranking' },
      { step: '04', title: 'Context Compression', description: 'Long-context summarization & token pruning before generation' }
    ]
  },
  {
    id: 'finetuner',
    title: 'Fine-Tuning Mastery',
    badge: 'PEFT, LoRA & Post-Training',
    subtitle: 'Train Custom Open-Weights Models with Unsloth & DPO',
    description: 'Take full control of open-source weights (Llama 3, DeepSeek-R1, Mistral). Master Supervised Fine-Tuning (SFT), Direct Preference Optimization (DPO), QLoRA 4-bit quantization, and synthetic dataset generation.',
    gradient: 'from-purple-500/20 via-indigo-500/10 to-transparent',
    accentColor: 'text-purple-400',
    borderColor: 'border-purple-500/30',
    iconName: 'Cpu',
    skills: [
      'Unsloth & Axolotl 2x Faster Fine-tuning with 60% Memory Reduction',
      'PEFT, QLoRA, Rank-Stabilized LoRA (rsLoRA) & Adapters Merging',
      'Direct Preference Optimization (DPO) & Alignment Tuning (RLHF/ORPO)',
      'Synthetic Dataset Curation & Distillation using DeepSeek-R1',
      'Model Quantization (GGUF, AWQ, EXL2) for Edge & Server Deployment'
    ],
    techStack: [
      { name: 'Unsloth', logo: '🦥' },
      { name: 'Hugging Face', logo: '🤗' },
      { name: 'Axolotl', logo: '🦎' },
      { name: 'TRL / DPO', logo: '🎯' },
      { name: 'DeepSeek', logo: '🐋' },
      { name: 'PyTorch', logo: '🔥' }
    ],
    capstoneProject: {
      title: 'Fine-Tuned Specialized Code Synthesis Model on Single A100 GPU',
      description: 'Distill DeepSeek-R1 reasoning trajectories into Llama-3-8B using QLoRA & DPO. Benchmark against GPT-4o on HumanEval coding tasks.',
      deliverables: ['Custom GGUF/AWQ model weight weights', '84.2% HumanEval Pass@1 score', 'Fully automated SFT + DPO training pipeline']
    },
    codeSnippet: {
      filename: 'unsloth_qlora_dpo.py',
      language: 'python',
      code: `from unsloth import FastLanguageModel
import torch
from trl import DPOTrainer, DPOConfig

# Step 1: Load 4-bit Quantized Base Model (DeepSeek / Llama-3-8B)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.1-8B-Instruct",
    max_seq_length=8192,
    load_in_4bit=True
)

# Step 2: Apply LoRA Target Modules
model = FastLanguageModel.get_peft_model(
    model,
    r=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=64,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth"
)

# Step 3: Run DPO Preference Optimization
trainer = DPOTrainer(
    model=model, ref_model=None,
    args=DPOConfig(per_device_train_batch_size=2, learning_rate=5e-6, beta=0.1),
    train_dataset=synthetic_dpo_dataset
)
trainer.train()`,
      output: '✓ VRAM Peak: 14.2 GB / 24 GB | Training Loss: 0.142 | Perplexity: 1.89'
    },
    architectureFlow: [
      { step: '01', title: 'Data Curation', description: 'De-duplication, toxicity filtering & synthetic seed prompt generation' },
      { step: '02', title: 'SFT Training', description: 'Supervised Fine-Tuning with 4-bit QLoRA and FlashAttention-2' },
      { step: '03', title: 'Alignment (DPO)', description: 'Direct Preference Optimization for domain tone and accuracy control' },
      { step: '04', title: 'Quantization', description: 'Exporting trained adapter to FP16, AWQ & GGML for inference engines' }
    ]
  },
  {
    id: 'evals',
    title: 'LLM Evals & Quality',
    badge: 'Evaluation & Guardrails',
    subtitle: 'Automate LLM Testing, Hallucination Checks & Red-Teaming',
    description: 'Transition from "vibes-based" AI development to rigorous engineering. Build automated evaluation pipelines, custom judge frameworks, assertion suites, and continuous guardrails that block bad outputs before users ever see them.',
    gradient: 'from-cyan-500/20 via-blue-500/10 to-transparent',
    accentColor: 'text-cyan-400',
    borderColor: 'border-cyan-500/30',
    iconName: 'ShieldCheck',
    skills: [
      'Ragas, DeepEval & TruLens Metrics Frameworks',
      'LLM-as-a-Judge Design & De-biasing Evaluation Models',
      'Automated Red-Teaming & Adversarial Jailbreak Defense',
      'CI/CD Prompt & Weight Regression Suites in GitHub Actions',
      'NeMo Guardrails & Llama Guard Real-Time Content Filtering'
    ],
    techStack: [
      { name: 'DeepEval', logo: '🧪' },
      { name: 'Ragas', logo: '📊' },
      { name: 'TruLens', logo: '🔍' },
      { name: 'NeMo Guard', logo: '🛡️' },
      { name: 'Promptfoo', logo: '⚡' },
      { name: 'MLflow', logo: '📈' }
    ],
    capstoneProject: {
      title: 'Enterprise AI Quality & Guardrail Suite in CI/CD Pipeline',
      description: 'Implement automated regression testing for hallucination, answer relevancy, toxicity, and PII leakage that triggers on every PR push.',
      deliverables: ['Automated PR blocking quality gates', 'Dashboard with real-time drift tracking', '100+ synthetic red-teaming test suites']
    },
    codeSnippet: {
      filename: 'eval_suite_test.py',
      language: 'python',
      code: `import pytest
from deepeval import assert_test
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

def test_rag_pipeline_accuracy():
    input_prompt = "What were Acme Corp's Q3 cloud revenues and profit margins?"
    actual_output = "Acme Corp reported $420M in Q3 cloud revenue with a 28% operating margin."
    retrieved_context = ["Acme Q3 SEC Filing: Cloud revenue reached $420 million, operating margin standing at 28.1%."]

    test_case = LLMTestCase(
        input=input_prompt,
        actual_output=actual_output,
        retrieval_context=retrieved_context
    )

    # Rigorous Multi-Metric Assertions
    hallucination_metric = HallucinationMetric(threshold=0.05)
    faithfulness_metric = FaithfulnessMetric(threshold=0.90)

    assert_test(test_case, [hallucination_metric, faithfulness_metric])`,
      output: '✓ Test Passed: Faithfulness 0.98 (>0.90 threshold) | Hallucination Score: 0.00'
    },
    architectureFlow: [
      { step: '01', title: 'Test Case Generation', description: 'Curating golden datasets and edge-case adversarial prompts' },
      { step: '02', title: 'Multi-Metric Benchmarking', description: 'Running Faithfulness, Answer Relevancy & Context Recall metrics' },
      { step: '03', title: 'LLM-as-a-Judge', description: 'Employing calibrated jury models with chain-of-thought verification' },
      { step: '04', title: 'Guardrail Enforcement', description: 'Real-time output scanning with regex, vector classifiers & toxic filters' }
    ]
  },
  {
    id: 'opsllm',
    title: 'OpsLLM & Infrastructure',
    badge: 'Production Latency & Scaling',
    subtitle: 'Deploy High-Throughput Engine Nodes with vLLM & Ray',
    description: 'Scale LLM production serving to thousands of requests per second. Master vLLM continuous batching, PagedAttention, TensorRT-LLM, Ray Serve clusters, streaming latency optimization, GPU cost reduction, and token token-bucket throttling.',
    gradient: 'from-emerald-500/20 via-teal-500/10 to-transparent',
    accentColor: 'text-emerald-400',
    borderColor: 'border-emerald-500/30',
    iconName: 'Server',
    skills: [
      'vLLM & TensorRT-LLM Engine Deployment with Continuous Batching',
      'PagedAttention & KV Cache Memory Management',
      'Multi-GPU Cluster Orchestration with Ray Serve & Kubernetes (K8s)',
      'TTFT (Time-To-First-Token) & Inference Latency Optimization (<40ms)',
      'Token Rate Limiting, Cost Budgeting & Intelligent Model Routing'
    ],
    techStack: [
      { name: 'vLLM', logo: '🚀' },
      { name: 'Ray Serve', logo: '☀️' },
      { name: 'TensorRT-LLM', logo: '🟢' },
      { name: 'Ollama', logo: '🦙' },
      { name: 'Kubernetes', logo: '☸️' },
      { name: 'Triton', logo: '⚡' }
    ],
    capstoneProject: {
      title: 'High-Throughput Multi-Node vLLM Cluster with Dynamic Scaling',
      description: 'Deploy a resilient model cluster handling 1,200 requests/second under sub-50ms TTFT latency with autoscaling GPU nodes on Kubernetes.',
      deliverables: ['Production K8s + Helm deployment configs', 'Prometheus & Grafana telemetry dashboards', '70% GPU cost reduction benchmark']
    },
    codeSnippet: {
      filename: 'deploy_vllm_ray.py',
      language: 'python',
      code: `import ray
from ray import serve
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams

@serve.deployment(num_replicas=4, ray_actor_options={"num_gpus": 2})
class VLLMDeployment:
    def __init__(self):
        engine_args = AsyncEngineArgs(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
            tensor_parallel_size=2,
            max_model_len=16384,
            gpu_memory_utilization=0.92,
            enable_chunked_prefill=True,
            quantization="awq"
        )
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    async def __call__(self, request) -> dict:
        data = await request.json()
        sampling_params = SamplingParams(temperature=0.2, max_tokens=1024)
        results_generator = self.engine.generate(data["prompt"], sampling_params, request.id)
        
        async for output in results_generator:
            if output.finished:
                return {"text": output.outputs[0].text, "tokens_per_sec": output.metrics.tokens_per_sec}`,
      output: '✓ Active Nodes: 4x 2xA100 (8 GPUs) | Throughput: 1,420 tokens/sec | TTFT: 32ms'
    },
    architectureFlow: [
      { step: '01', title: 'Model Packaging', description: 'AWQ/GPTQ weight loading & PagedAttention KV cache configuration' },
      { step: '02', title: 'Tensor Parallelism', description: 'Sharding model parameters across multiple GPU devices using NVLink' },
      { step: '03', title: 'Dynamic Batching', description: 'Continuous batching & chunked prefill for optimal GPU core saturation' },
      { step: '04', title: 'Telemetry & Route', description: 'Streaming SSE responses, prometheus metrics & token fallback routing' }
    ]
  }
];

export const EMPLOYERS = [
  { name: 'Coca-Cola', logo: 'coca-cola.png' },
  { name: 'Apple', logo: 'apple.png' },
  { name: 'Beehiiv', logo: 'beehiiv.png' },
  { name: 'Strike', logo: 'strike.png' },
  { name: 'PayPal', logo: 'paypal.png' },
  { name: 'X-Team', logo: 'x-team.png' },
  { name: 'Pizza Hut', logo: 'pizza-hut.png' },
  { name: 'Accenture', logo: 'accenture.png' },
  { name: 'Nubank', logo: 'nubank.png' },
  { name: 'BTG Pactual', logo: 'btg-pactual.png' },
] as const;

export const TESTIMONIALS = [
  {
    name: 'Alexandre Chen',
    role: 'Senior AI Systems Engineer @ Scale AI',
    formerRole: 'Senior Backend Developer (Ex-Fintech)',
    increase: '+$95,000 / yr',
    company: 'Scale AI',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
    quote: 'Career Forge bridges the gap between basic API wrapper tutorials and real high-scale AI engineering. The vLLM continuous batching and DPO fine-tuning labs directly helped me clear my senior staff loop at Scale AI.',
    verifiedBadge: 'Cohort 9 Graduate',
    metrics: { beforeSalary: '$165,000', afterSalary: '$260,000', paybackDays: '34 days' }
  },
  {
    name: 'Sarah Jenkins',
    role: 'Staff LLM Platform Lead @ Databricks',
    formerRole: 'Full-Stack Software Engineer',
    increase: '+$110,000 / yr',
    company: 'Databricks',
    avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=150&q=80',
    quote: 'I went from writing basic OpenAI prompts to architecting multi-GPU vLLM clusters with automated DeepEval regression suites. The code reviews from ex-OpenAI engineers were brutal in the best possible way!',
    verifiedBadge: 'Cohort 10 Graduate',
    metrics: { beforeSalary: '$180,000', afterSalary: '$290,000', paybackDays: '28 days' }
  },
  {
    name: 'Dimitri Rostov',
    role: 'Lead AI Engineer @ Series B AI Startup',
    formerRole: 'Data Engineer @ Enterprise Tech',
    increase: '+$78,000 / yr',
    company: 'Nexus AI',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80',
    quote: 'The GraphRAG capstone project alone got me 4 job offers. Showing hiring managers a live vector DB with RRF reranking and latency under 150ms instantly proved I was in the top 1% of applicants.',
    verifiedBadge: 'Cohort 11 Graduate',
    metrics: { beforeSalary: '$142,000', afterSalary: '$220,000', paybackDays: '42 days' }
  },
  {
    name: 'Elena Rostova',
    role: 'Founding AI Engineer @ Stealth AI',
    formerRole: 'Frontend Lead turned AI Specialist',
    increase: '+$88,000 / yr',
    company: 'Stealth AI',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80',
    quote: 'Understanding quantizations (AWQ vs GGUF) and DPO dataset curation allowed us to drop our monthly cloud LLM API bill from $40k to $6k while speeding up response times 3x.',
    verifiedBadge: 'Cohort 8 Graduate',
    metrics: { beforeSalary: '$155,000', afterSalary: '$243,000', paybackDays: '38 days' }
  }
];

export const MENTORS = [
  {
    name: 'Yuri Pereira',
    role: 'Founder and Strategic Tech Advisor',
    bio: 'Founded Borderless Coding in 2023. Strategic tech advisor for the BASE and PSP ecosystem that Career Forge sits in.',
    avatar: 'yuri.webp',
    specialty: 'Founder',
  },
  {
    name: 'Pedro Alano',
    role: 'Founder Engineer',
    bio: 'Software engineer. Builds Career Forge with the Borderless team.',
    avatar: 'pedro.png',
    specialty: 'Career Forge',
  },
];

export const ROADMAP_WEEKS = [
  {
    week: 'Weeks 1-3',
    phase: 'Phase 1: Advanced RAG & Vector Systems',
    title: 'Retrieval Engineering, GraphRAG & Semantic Cache',
    topics: ['Dense vs Sparse Embeddings', 'Reciprocal Rank Fusion (RRF)', 'Hierarchical Chunking', 'GraphRAG with Neo4j', 'Semantic Caching'],
    project: 'Build a production multi-tenant hybrid RAG engine with sub-200ms latency',
    tech: ['Qdrant', 'LlamaIndex', 'Cohere Rerank', 'Redis']
  },
  {
    week: 'Weeks 4-6',
    phase: 'Phase 2: Open-Weights Fine-Tuning (SFT & DPO)',
    title: 'PEFT, QLoRA, Axolotl & Synthetic Alignment',
    topics: ['Supervised Fine-Tuning (SFT)', 'Direct Preference Optimization (DPO)', '4-bit Quantization', 'DeepSeek-R1 Distillation', 'Dataset Cleaning'],
    project: 'Fine-tune Llama 3 on domain code synthesis and distill reasoning weights',
    tech: ['Unsloth', 'Axolotl', 'Hugging Face TRL', 'PyTorch']
  },
  {
    week: 'Weeks 7-9',
    phase: 'Phase 3: Automated Evals & Guardrails',
    title: 'CI/CD Evals, Hallucination Checks & Red Teaming',
    topics: ['Ragas & DeepEval Metrics', 'LLM-as-a-Judge Jury Calibration', 'Adversarial Jailbreaks', 'NeMo Guardrails', 'Regression Gateways'],
    project: 'Integrate automated prompt & weight regression testing into GitHub Actions',
    tech: ['DeepEval', 'Ragas', 'NeMo Guardrails', 'Promptfoo']
  },
  {
    week: 'Weeks 10-12',
    phase: 'Phase 4 & 5: OpsLLM, High-Throughput Cluster & Capstone Launch',
    title: 'vLLM, Ray Serve, Latency Tuning & Hiring Showcase',
    topics: ['PagedAttention & Continuous Batching', 'Multi-GPU Tensor Parallelism', 'Ray Serve Clustering', 'TTFT Optimization', 'Demo Day to Tech Partners'],
    project: 'Deploy multi-node autoscaling vLLM engine handling 1000+ RPS + Capstone Demo',
    tech: ['vLLM', 'Ray Serve', 'Kubernetes', 'Prometheus']
  }
];

export const PRICING_PLANS = [
  {
    id: 'members',
    name: 'BASE · PSP',
    badge: 'Members',
    price: 'Included',
    period: 'with your member email',
    description:
      'Career Forge is included for BASE and PSP learners. Start diagnosis with your member email.',
    popular: false,
    features: [
      'Diagnosis before any roadmap',
      'Live Roadmap Forge for your track',
      'Mastery validation on the trail',
      'Four LLM tracks: RAG, Fine-Tuning, Evals, OpsLLM',
      'No Stripe for BASE and PSP members',
    ],
    ctaText: 'Start diagnosis',
  },
  {
    id: 'external',
    name: 'External',
    badge: 'Most common path',
    price: '$10–15',
    period: 'per month, billed in-product after Email identity',
    description:
      'Unpaid external learners see USD $10–15/mo after Email identity. Billing stays in the product — not on this page.',
    popular: true,
    features: [
      'Same product loop after Email identity',
      'USD $10–15/mo Labs band (no fake point price here)',
      'Billed in-loop after OTP — not Stripe on Welcome',
      'BASE and PSP stay included if you are a member',
    ],
    ctaText: 'Start diagnosis',
  },
];

export const FAQS = [
  {
    category: 'Membership',
    question: 'Who is Career Forge for?',
    answer:
      'BASE and PSP members: Career Forge is included. Start diagnosis with your member email. Others (unpaid external) see USD $10–15/mo after Email identity, billed in the product — not as checkout on this page.',
  },
  {
    category: 'Product',
    question: 'Why is this not a prompt course?',
    answer:
      'No. It is not a prompt course. Career Forge diagnoses your starting point, forges a live roadmap for a production-AI track (RAG, Fine-Tuning, Evals, or OpsLLM), and validates mastery before you move on.',
  },
  {
    category: 'Start',
    question: 'How do I start?',
    answer:
      'Click Start diagnosis. You confirm Email identity (OTP) at product entry, then the loop is goal → diagnosis → Live Forge → roadmap → validate mastery.',
  },
  {
    category: 'Product',
    question: 'What does the product do?',
    answer:
      'Diagnosis maps where you are before any roadmap exists. Live Forge lets you watch that roadmap take shape. Validate mastery checks what you can actually do; the trail reacts to evidence.',
  },
  {
    category: 'Hardware',
    question: 'Do I need a GPU or NVIDIA credits?',
    answer:
      'No. You work from your laptop. Career Forge does not include NVIDIA or cloud GPU credits.',
  },
  {
    category: 'Guarantees',
    question: 'Is there a job or refund guarantee?',
    answer:
      'No. Career Forge does not guarantee a job, a salary lift, or a refund.',
  },
];
