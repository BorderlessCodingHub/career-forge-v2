"use client";

import { XCircle, CheckCircle2, AlertTriangle, ArrowRight, Flame, ShieldAlert } from 'lucide-react';
import Link from "next/link";

export function IndustryProblem() {
  return (
    <section className="py-20 bg-slate-950 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-semibold uppercase tracking-wider mb-4">
            <AlertTriangle className="w-3.5 h-3.5" />
            The 2026 AI Engineering Imperative
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            Basic API Wrappers Are Dead.{' '}
            <span className="gradient-text-orange">Companies Demand AI Systems Engineers.</span>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
            In 2026, gluing together a quick `openai.ChatCompletion` call with default settings won't get you hired or promoted. Top tech companies need engineers who can lower cloud GPU bills, prevent hallucinations, fine-tune custom domain models, and scale inference.
          </p>
        </div>

        {/* Comparison Cards Grid */}
        <div className="grid md:grid-cols-2 gap-8 items-stretch mb-12">
          
          {/* Card 1: The Generic Developer */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-red-500/20 bg-gradient-to-b from-red-950/20 via-slate-900 to-slate-950 relative">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-red-500/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center justify-center">
                  <ShieldAlert className="w-5 h-5 text-red-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Generic Software Engineer</h3>
                  <p className="text-xs text-red-400 font-mono">Stuck at API Wrapper Tier</p>
                </div>
              </div>
              <span className="text-xs font-bold text-slate-400 bg-slate-800 px-2.5 py-1 rounded">
                Avg: $130k - $160k
              </span>
            </div>

            <ul className="space-y-4 text-sm text-slate-300">
              <li className="flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Naive Prompting & Naive Vector Search:</strong> High hallucination rate, struggles with complex multi-step reasoning, poor precision.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <span>
                  <strong>"Vibes-Based" Testing:</strong> Manually re-running prompts in ChatGPT UI to see if it "looks good" instead of building continuous CI/CD evaluation suites.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <span>
                  <strong>100% Locked to Commercial API Costs:</strong> Paying $40,000/month for closed API tokens without knowing how to fine-tune open models for 80% cost savings.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Slow & Unscalable Endpoints:</strong> Blocked by API rate limits, slow 2+ second latency, no continuous batching or KV cache management.
                </span>
              </li>
            </ul>
          </div>

          {/* Card 2: The Career Forge Trained AI Specialist */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-emerald-500/40 bg-gradient-to-b from-emerald-950/30 via-slate-900 to-slate-950 relative shadow-2xl shadow-emerald-500/10">
            <div className="absolute -top-3 right-6 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-xs px-3 py-1 rounded-full uppercase tracking-wider shadow">
              CAREER FORGE CERTIFIED
            </div>

            <div className="flex items-center justify-between mb-6 pb-4 border-b border-emerald-500/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
                  <Flame className="w-5 h-5 text-emerald-400 fill-emerald-400/20" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Forge AI Systems Engineer</h3>
                  <p className="text-xs text-emerald-400 font-mono">Master of RAG, Fine-Tuning, Evals & OpsLLM</p>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-300 bg-emerald-950/80 border border-emerald-500/40 px-2.5 py-1 rounded font-mono">
                Avg: $240k - $380k+
              </span>
            </div>

            <ul className="space-y-4 text-sm text-slate-200">
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-white">Hybrid GraphRAG Architectures:</strong> Dense + Sparse RRF indexing, Cohere Rerank v3, and agentic self-corrective retrieval with 98%+ precision.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-white">Unsloth SFT & DPO Fine-Tuning:</strong> Fine-tune Llama 3 & DeepSeek weights with 4-bit QLoRA, custom preference alignment, and synthetic dataset curation.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-white">Automated DeepEval CI/CD Quality Gates:</strong> Measure Faithfulness, Hallucination score, Toxicity, and PR regression before code hits production.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-white">High-Throughput vLLM & Ray Serve Ops:</strong> Deploy multi-GPU engine nodes with PagedAttention, continuous batching, and sub-40ms TTFT latency.
                </span>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Action Line */}
        <div className="text-center">
          <Link
            href="/"
            data-testid="welcome-cta-start"
            aria-label="Start diagnosis"
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-orange-500 via-amber-500 to-indigo-600 rounded-xl text-white font-extrabold text-sm shadow-xl hover:shadow-orange-500/25 transition-all cursor-pointer"
          >
            <span>Start here</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

      </div>
    </section>
  );
};
