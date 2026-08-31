"use client";

import { TESTIMONIALS } from './data/curriculumData';
import { CheckCircle, Sparkles } from 'lucide-react';
import { welcomeAssetPath } from "@/lib/welcome-assets";

export function Testimonials() {
  return (
    <section id="testimonials" className="py-24 bg-slate-950 border-t border-slate-900 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-bold uppercase tracking-wider mb-4 font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            BASE · PSP SUCCESS STORIES
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            See How Engineers <span className="gradient-text-orange">Transformed Their Careers</span> with <span className="gradient-text-purple">Borderless</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Named mentees from Borderless BASE and PSP — the ecosystem Career Forge is built for. These outcomes are from mentorship, published on borderlesscoding.com.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {TESTIMONIALS.map((t) => (
            <div
              key={t.name}
              className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 bg-slate-900/80 hover:border-slate-700 transition-all flex flex-col justify-between shadow-xl relative"
            >
              <div>
                {/* Header info */}
                <div className="flex items-start justify-between gap-4 mb-6">
                  <div className="flex items-center gap-3">
                    {/* eslint-disable-next-line @next/next/no-img-element -- local Welcome testimonial photos */}
                    <img
                      src={welcomeAssetPath("testimonials", t.avatar)}
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

                  <div className="bg-slate-950 border border-slate-700 text-orange-300 px-3 py-1 rounded-xl text-xs font-mono font-extrabold text-right shrink-0">
                    {t.program}
                  </div>
                </div>

                {/* Case study — third-person copy from Borderless, not a first-person quote */}
                <p className="text-sm text-slate-200 leading-relaxed mb-6">
                  {t.story}
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
              </div>

            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
