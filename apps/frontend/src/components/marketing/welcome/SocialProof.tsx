"use client";

import { useState, useEffect } from "react";

const RECENT_OFFERS = [
  { name: 'Michael K.', role: 'Senior RAG Systems Engineer', company: 'Scale AI', salary: '$275,000', location: 'San Francisco, CA' },
  { name: 'Priya R.', role: 'LLM Fine-Tuning Lead', company: 'Databricks', salary: '$290,000', location: 'Remote / US' },
  { name: 'David W.', role: 'AI Platform Infrastructure Engineer', company: 'Stripe', salary: '$265,000', location: 'Seattle, WA' },
  { name: 'Elena V.', role: 'OpsLLM & Inference Specialist', company: 'Anthropic', salary: '$310,000', location: 'San Francisco, CA' },
  { name: 'Jordan B.', role: 'Founding AI Architect', company: 'Stealth AI Series A', salary: '$240,000 + 1.2% Equity', location: 'New York, NY' }
] as const;

export function SocialProof() {
  const [tickerIndex, setTickerIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setTickerIndex((prev) => (prev + 1) % RECENT_OFFERS.length);
    }, 3800);
    return () => clearInterval(timer);
  }, []);

  const currentOffer = RECENT_OFFERS[tickerIndex];

  return (
    <section className="py-12 bg-slate-950/90 border-y border-slate-800/80 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Ticker: Live Verified Salary & Placement Feed */}
        <div className="max-w-3xl mx-auto mb-10">
          <div className="glass-panel p-3.5 sm:p-4 rounded-xl border border-indigo-500/20 bg-slate-900/80 flex flex-wrap items-center justify-between gap-3 shadow-xl">
            <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span>LIVE ALUMNI OFFER FEED</span>
            </div>

            <div className="flex-1 min-w-[240px] text-xs font-medium text-slate-200 transition-all duration-500 flex items-center justify-between gap-2">
              <div className="truncate">
                <span className="font-bold text-white">{currentOffer.name}</span> accepted{' '}
                <span className="text-orange-300 font-semibold">{currentOffer.role}</span> at{' '}
                <span className="text-indigo-300 font-bold">{currentOffer.company}</span>
              </div>
              <div className="font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30 whitespace-nowrap">
                {currentOffer.salary}
              </div>
            </div>
          </div>
        </div>

        {/* Company Logos Heading */}
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-slate-400 mb-8">
          Our Graduates Engineer LLMs & RAG Infrastructure At Leading Tech Companies
        </p>

        {/* Brand Logos Wall */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-4 items-center justify-center opacity-80 hover:opacity-100 transition-opacity">
          {[
            { name: 'OpenAI', badge: 'GPT-4o & Evals' },
            { name: 'Anthropic', badge: 'Claude Ops' },
            { name: 'Databricks', badge: 'Vector Search' },
            { name: 'Stripe', badge: 'LLM Risk' },
            { name: 'Meta AI', badge: 'Llama 3 SFT' },
            { name: 'Scale AI', badge: 'RLHF Data' },
            { name: 'Snowflake', badge: 'Cortex AI' },
            { name: 'Palantir', badge: 'AIP Infrastructure' }
          ].map((item, index) => (
            <div
              key={index}
              className="glass-panel p-3 rounded-lg border border-slate-800 text-center hover:border-slate-700 hover:bg-slate-900 transition-all group"
            >
              <div className="font-extrabold text-sm sm:text-base text-slate-200 group-hover:text-white font-mono tracking-tight">
                {item.name}
              </div>
              <div className="text-[10px] text-slate-400 group-hover:text-orange-400 font-mono mt-0.5">
                {item.badge}
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
};
