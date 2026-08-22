"use client";

import { useState } from "react";
import { TESTIMONIALS } from './data/curriculumData';
import { Star, CheckCircle, Sparkles } from 'lucide-react';

export function Testimonials() {
  const [activeFilter, setActiveFilter] = useState<string>('all');

  const filteredTestimonials = activeFilter === 'all'
    ? TESTIMONIALS
    : TESTIMONIALS.filter(t => t.formerRole.toLowerCase().includes(activeFilter));

  return (
    <section id="testimonials" className="py-24 bg-slate-950 border-t border-slate-900 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-bold uppercase tracking-wider mb-4 font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            VERIFIED ALUMNI TRANSFORMATIONS
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            See How 640+ Engineers <span className="gradient-text-orange">Transformed Their Careers</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Real software developers who used the RAG, fine-tuning, and vLLM capstones to land lead AI roles at Scale AI, Databricks, Stripe, and high-growth startups.
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="flex flex-wrap justify-center gap-2 mb-12">
          {[
            { id: 'all', label: 'All Graduates' },
            { id: 'backend', label: 'Backend Developers' },
            { id: 'full-stack', label: 'Full-Stack' },
            { id: 'data', label: 'Data Engineers' }
          ].map((btn) => (
            <button
              key={btn.id}
              onClick={() => setActiveFilter(btn.id)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold font-mono transition-all cursor-pointer border ${
                activeFilter === btn.id
                  ? 'bg-orange-500 text-slate-950 font-bold border-orange-400 shadow-lg'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              {btn.label}
            </button>
          ))}
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {filteredTestimonials.map((t, index) => (
            <div
              key={index}
              className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 bg-slate-900/80 hover:border-slate-700 transition-all flex flex-col justify-between shadow-xl relative"
            >
              <div>
                {/* Header info */}
                <div className="flex items-start justify-between gap-4 mb-6">
                  <div className="flex items-center gap-3">
                    <img
                      src={t.avatar}
                      alt={t.name}
                      className="w-14 h-14 rounded-full object-cover border-2 border-orange-500/40"
                    />
                    <div>
                      <h3 className="text-lg font-bold text-white flex items-center gap-1.5">
                        <span>{t.name}</span>
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      </h3>
                      <div className="text-xs text-orange-400 font-bold font-mono">
                        {t.role}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Prior: {t.formerRole}
                      </div>
                    </div>
                  </div>

                  <div className="bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 px-3 py-1 rounded-xl text-xs font-mono font-extrabold text-right shrink-0">
                    <div>{t.increase}</div>
                    <div className="text-[10px] text-emerald-400 font-normal">Compensation Boost</div>
                  </div>
                </div>

                {/* Stars */}
                <div className="flex items-center gap-1 mb-4 text-yellow-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400" />
                  ))}
                </div>

                {/* Quote */}
                <p className="text-sm text-slate-200 leading-relaxed italic mb-6">
                  "{t.quote}"
                </p>
              </div>

              {/* Metrics Bar */}
              <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
                <div className="flex items-center gap-2 text-slate-400">
                  <span className="text-slate-500">Trajectory:</span>
                  <span className="text-slate-300 font-bold">{t.metrics.beforeSalary}</span>
                  <span className="text-orange-400">→</span>
                  <span className="text-emerald-400 font-bold">{t.metrics.afterSalary}</span>
                </div>
                <div className="bg-slate-950 px-2.5 py-1 rounded border border-slate-800 text-[11px] text-slate-400">
                  Payback: <strong className="text-white">{t.metrics.paybackDays}</strong>
                </div>
              </div>

            </div>
          ))}
        </div>

      </div>
    </section>
  );
};
