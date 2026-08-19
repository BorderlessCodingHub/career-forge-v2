import React from 'react';
import { PRICING_PLANS } from '../data/curriculumData';
import { ShieldCheck, Sparkles, ArrowRight, Gift } from 'lucide-react';

interface PricingProps {
  onOpenApplyModal: () => void;
  onOpenSyllabusModal: () => void;
  onOpenStrategyModal: () => void;
}

export const Pricing: React.FC<PricingProps> = ({
  onOpenApplyModal,
  onOpenStrategyModal
}) => {

  return (
    <section id="pricing" className="py-24 bg-slate-950 border-t border-slate-900 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-bold uppercase tracking-wider mb-4 font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            TRANSPARENT TUITION & SCHOLARSHIP
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            Invest in High-Leverage <span className="gradient-text-orange">AI Mastery</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Guaranteed ROI. Average alumni recoup tuition in less than 32 days of employment at their new salary tier.
          </p>
        </div>

        {/* Early Bird Scholarship Banner */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="glass-panel p-5 rounded-2xl border border-orange-500/40 bg-gradient-to-r from-orange-950/60 via-slate-900 to-indigo-950/60 flex flex-wrap items-center justify-between gap-4 shadow-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-orange-500/20 border border-orange-500/40 flex items-center justify-center shrink-0">
                <Gift className="w-5 h-5 text-orange-400" />
              </div>
              <div>
                <div className="text-sm font-bold text-white flex items-center gap-2">
                  <span>Cohort 12 Early Bird Scholarship Active</span>
                  <span className="bg-orange-500 text-slate-950 text-[10px] font-mono px-2 py-0.5 rounded font-extrabold">
                    SAVE $500
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-0.5">
                  Includes <strong>$500 Nvidia Cloud GPU Credits</strong> + Lifetime access to DeepSeek-R1 & Llama 3 upgrades.
                </p>
              </div>
            </div>
            <button
              onClick={onOpenApplyModal}
              className="px-5 py-2.5 bg-orange-500 hover:bg-orange-400 text-slate-950 font-mono font-extrabold text-xs rounded-xl shadow transition-all cursor-pointer whitespace-nowrap"
            >
              Claim $500 Discount →
            </button>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid lg:grid-cols-3 gap-8 max-w-7xl mx-auto items-stretch">
          {PRICING_PLANS.map((plan) => {
            const isPopular = plan.popular;
            return (
              <div
                key={plan.id}
                className={`glass-panel rounded-3xl p-6 sm:p-8 flex flex-col justify-between transition-all relative border ${
                  isPopular
                    ? 'border-orange-500/60 bg-gradient-to-b from-slate-900 via-slate-900 to-indigo-950/40 shadow-2xl ring-2 ring-orange-500/30'
                    : 'border-slate-800 bg-slate-900/80 hover:border-slate-700'
                }`}
              >
                {isPopular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-gradient-to-r from-orange-500 to-amber-500 text-slate-950 font-extrabold text-[11px] font-mono px-4 py-1 rounded-full uppercase tracking-wider shadow-lg">
                    {plan.badge}
                  </div>
                )}

                <div>
                  {!isPopular && (
                    <div className="text-xs font-mono font-bold text-slate-400 mb-2 uppercase tracking-wider">
                      {plan.badge}
                    </div>
                  )}

                  <h3 className="text-2xl font-extrabold text-white mb-2">
                    {plan.name}
                  </h3>

                  <p className="text-xs text-slate-300 leading-relaxed mb-6">
                    {plan.description}
                  </p>

                  <div className="mb-6 pb-6 border-b border-slate-800">
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl sm:text-5xl font-extrabold text-white font-mono">
                        {plan.price}
                      </span>
                    </div>
                    <div className="text-xs text-orange-400 font-mono font-semibold mt-1">
                      {plan.period}
                    </div>
                  </div>

                  {/* Feature Checklist */}
                  <div className="space-y-3 mb-8">
                    <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
                      INCLUDED IN THIS PLAN:
                    </div>
                    {plan.features.map((feat, i) => (
                      <div key={i} className="flex items-start gap-3 text-xs text-slate-200">
                        <div className={`w-4 h-4 rounded-full ${isPopular ? 'bg-orange-500 text-slate-950' : 'bg-slate-800 text-indigo-400'} flex items-center justify-center shrink-0 mt-0.5 text-[10px] font-bold`}>
                          ✓
                        </div>
                        <span className={feat.startsWith('Everything') || feat.includes('PLUS') ? 'font-bold text-white' : ''}>
                          {feat}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Card Footer CTA */}
                <div>
                  <button
                    onClick={plan.id === 'enterprise' ? onOpenStrategyModal : onOpenApplyModal}
                    className={`w-full py-4 rounded-xl font-extrabold text-xs uppercase tracking-wider shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer ${
                      isPopular
                        ? 'bg-gradient-to-r from-orange-500 via-amber-500 to-indigo-600 text-white hover:shadow-orange-500/30'
                        : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                    }`}
                  >
                    <span>{plan.ctaText}</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>

                  <div className="mt-3 text-center flex items-center justify-center gap-1.5 text-[11px] text-slate-400 font-mono">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{plan.guarantee}</span>
                  </div>
                </div>

              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};
