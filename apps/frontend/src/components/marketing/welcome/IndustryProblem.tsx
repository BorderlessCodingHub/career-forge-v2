"use client";

import { XCircle, CheckCircle2, AlertTriangle, ArrowRight, Flame, ShieldAlert } from 'lucide-react';
import Link from "next/link";
import { useWelcomeText } from "./useWelcomeText";

export function IndustryProblem() {
  const { text, list } = useWelcomeText();
  const generic = list<{ lead: string; body: string }>("problem.generic");
  const forge = list<{ lead: string; body: string }>("problem.forge");
  return (
    <section className="py-20 bg-slate-950 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-semibold uppercase tracking-wider mb-4">
            <AlertTriangle className="w-3.5 h-3.5" />
            {text("problem.eyebrow")}
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
            {text("problem.titleBefore")}{' '}
            <span className="gradient-text-orange">{text("problem.titleAccent")}</span>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
            {text("problem.lead")}
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
                  <h3 className="text-lg font-bold text-white">{text("problem.genericTitle")}</h3>
                  <p className="text-xs text-red-400 font-mono">{text("problem.genericSubtitle")}</p>
                </div>
              </div>
              <span className="text-xs font-bold text-slate-400 bg-slate-800 px-2.5 py-1 rounded">
                {text("problem.genericAvg")}
              </span>
            </div>

            <ul className="space-y-4 text-sm text-slate-300">
              {generic.map((item) => (
                <li key={item.lead} className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>{item.lead}</strong>
                    {item.body}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Card 2: The Career Forge Trained AI Specialist */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-emerald-500/40 bg-gradient-to-b from-emerald-950/30 via-slate-900 to-slate-950 relative shadow-2xl shadow-emerald-500/10">
            <div className="absolute -top-3 right-6 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-xs px-3 py-1 rounded-full uppercase tracking-wider shadow">
              {text("problem.certified")}
            </div>

            <div className="flex items-center justify-between mb-6 pb-4 border-b border-emerald-500/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
                  <Flame className="w-5 h-5 text-emerald-400 fill-emerald-400/20" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">{text("problem.forgeTitle")}</h3>
                  <p className="text-xs text-emerald-400 font-mono">{text("problem.forgeSubtitle")}</p>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-300 bg-emerald-950/80 border border-emerald-500/40 px-2.5 py-1 rounded font-mono">
                {text("problem.forgeAvg")}
              </span>
            </div>

            <ul className="space-y-4 text-sm text-slate-200">
              {forge.map((item) => (
                <li key={item.lead} className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  <span>
                    <strong className="text-white">{item.lead}</strong>
                    {item.body}
                  </span>
                </li>
              ))}
            </ul>
          </div>

        </div>

        {/* Bottom Action Line */}
        <div className="text-center">
          <Link
            href="/"
            data-testid="welcome-cta-start"
            aria-label={text("startDiagnosis")}
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-orange-500 via-amber-500 to-indigo-600 rounded-xl text-white font-extrabold text-sm shadow-xl hover:shadow-orange-500/25 transition-all cursor-pointer"
          >
            <span>{text("startHere")}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

      </div>
    </section>
  );
};
