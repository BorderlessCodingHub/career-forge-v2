import React from 'react';
import { Flame, ArrowRight, ShieldCheck, Clock } from 'lucide-react';

interface CtaSectionProps {
  onOpenApplyModal: () => void;
  onOpenStrategyModal: () => void;
}

export const CtaSection: React.FC<CtaSectionProps> = ({
  onOpenApplyModal,
  onOpenStrategyModal
}) => {
  return (
    <section className="py-24 bg-slate-950 relative overflow-hidden border-t border-slate-900">
      
      {/* Background Forge Light Orbs */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-gradient-to-tr from-orange-600/20 via-indigo-600/20 to-purple-600/15 rounded-full blur-[140px] pointer-events-none"></div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="glass-panel p-8 sm:p-14 rounded-3xl border border-orange-500/40 bg-gradient-to-b from-slate-900/90 via-slate-950 to-slate-950 text-center shadow-2xl relative overflow-hidden">
          
          {/* Top Forge Icon Badge */}
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-slate-950 border border-orange-500/50 shadow-xl shadow-orange-500/20 mb-6">
            <Flame className="w-8 h-8 text-orange-400 fill-orange-400/20 animate-pulse" />
          </div>

          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-6 leading-tight">
            Ready to Forge Your Career in <br className="hidden sm:inline" />
            <span className="gradient-text-hero">Production AI Engineering?</span>
          </h2>

          <p className="text-slate-300 text-base sm:text-xl max-w-2xl mx-auto mb-8 font-normal leading-relaxed">
            Stop gluing together basic OpenAI wrapper calls. Master RAG, Fine-Tuning, Evals, and OpsLLM to build enterprise-grade AI applications.
          </p>

          {/* Micro urgency items */}
          <div className="flex flex-wrap justify-center gap-4 text-xs sm:text-sm font-mono text-slate-300 mb-10">
            <div className="flex items-center gap-1.5 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
              <span className="w-2 h-2 rounded-full bg-orange-400 animate-ping"></span>
              <span>Next Cohort: <strong>April 14</strong></span>
            </div>
            <div className="flex items-center gap-1.5 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
              <Clock className="w-4 h-4 text-orange-400" />
              <span><strong>8 Seats Remaining</strong></span>
            </div>
            <div className="flex items-center gap-1.5 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>100% Risk-Free Guarantee</span>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto">
            <button
              onClick={onOpenApplyModal}
              className="w-full relative group px-8 py-4 rounded-xl font-extrabold text-base text-white shimmer-button shadow-2xl shadow-orange-500/30 hover:shadow-orange-500/50 transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Apply For Cohort 12 ($500 Off)</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={onOpenStrategyModal}
              className="w-full px-6 py-4 rounded-xl text-xs font-bold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-700 transition-colors cursor-pointer"
            >
              Book 1-on-1 Strategy Call
            </button>
          </div>

        </div>
      </div>
    </section>
  );
};
