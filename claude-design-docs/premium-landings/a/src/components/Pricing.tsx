import { useState } from 'react';
import { motion } from 'framer-motion';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { Check, Zap, Crown, Sparkles } from 'lucide-react';

const plans = [
  {
    name: 'Self-Paced',
    price: { monthly: 79, annual: 59 },
    description: 'Perfect for self-motivated learners who want flexibility.',
    icon: Zap,
    popular: false,
    features: [
      'Full 12-week curriculum',
      'All video lectures & materials',
      '12+ hands-on projects',
      'Community Discord access',
      'Certificate of completion',
      'Lifetime content updates',
    ],
    cta: 'Start Learning',
    color: 'from-brand-500/20 to-brand-600/20',
  },
  {
    name: 'Pro',
    price: { monthly: 199, annual: 149 },
    description: 'The complete experience with mentorship and career support.',
    icon: Crown,
    popular: true,
    features: [
      'Everything in Self-Paced',
      'Weekly 1-on-1 mentorship',
      'Code review by AI experts',
      'Career coaching sessions',
      'Job referral network',
      'Priority support',
      'Mock interview prep',
      'LinkedIn optimization',
    ],
    cta: 'Go Pro',
    color: 'from-brand-500/30 to-accent-500/30',
  },
  {
    name: 'Enterprise',
    price: { monthly: 449, annual: 349 },
    description: 'For teams looking to upskill in AI/LLM engineering.',
    icon: Sparkles,
    popular: false,
    features: [
      'Everything in Pro',
      'Team dashboard & analytics',
      'Custom curriculum modules',
      'Dedicated success manager',
      'On-demand workshops',
      'API access for integrations',
      'Bulk seat discounts',
      'Invoice billing',
    ],
    cta: 'Contact Sales',
    color: 'from-purple-500/20 to-pink-500/20',
  },
];

export default function Pricing() {
  const { ref, isVisible } = useScrollReveal();
  const [isAnnual, setIsAnnual] = useState(true);

  return (
    <section id="pricing" ref={ref} className="relative py-24 md:py-32 overflow-hidden">
      <div className="ambient-orb w-[600px] h-[600px] bg-brand-600/10 -bottom-40 left-1/3" style={{ animationDelay: '6s' }} />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-sm font-medium text-brand-300 mb-6"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
            Pricing
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight"
          >
            Invest in Your{' '}
            <span className="gradient-text">AI Future</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-5 text-lg text-surface-200/70"
          >
            Choose the plan that fits your learning style. All plans include our 30-day money-back guarantee.
          </motion.p>
        </div>

        {/* Billing toggle */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex items-center justify-center gap-4 mb-12"
        >
          <span className={`text-sm font-medium transition-colors ${!isAnnual ? 'text-white' : 'text-surface-200/50'}`}>Monthly</span>
          <button
            onClick={() => setIsAnnual(!isAnnual)}
            className="relative w-14 h-7 rounded-full bg-white/10 transition-colors hover:bg-white/15"
            aria-label="Toggle billing period"
          >
            <motion.div
              animate={{ x: isAnnual ? 28 : 2 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              className="absolute top-1 w-5 h-5 rounded-full bg-gradient-to-r from-brand-500 to-accent-500"
            />
          </button>
          <span className={`text-sm font-medium transition-colors ${isAnnual ? 'text-white' : 'text-surface-200/50'}`}>
            Annual
            <span className="ml-2 text-xs text-emerald-400 font-semibold">Save 25%</span>
          </span>
        </motion.div>

        {/* Pricing cards */}
        <div className="grid md:grid-cols-3 gap-6 lg:gap-8 items-start">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.3 + i * 0.1, duration: 0.6 }}
              className={`relative group ${plan.popular ? 'md:-mt-4 md:mb-4' : ''}`}
            >
              {/* Popular badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
                  <div className="px-4 py-1.5 rounded-full bg-gradient-to-r from-brand-500 to-accent-500 text-xs font-bold text-white uppercase tracking-wider shadow-lg shadow-brand-500/30">
                    Most Popular
                  </div>
                </div>
              )}

              <div className={`glass-card rounded-3xl p-6 md:p-8 transition-all duration-500 hover:scale-[1.02] ${
                plan.popular ? 'ring-2 ring-brand-500/30 shadow-2xl shadow-brand-500/10' : ''
              }`}>
                {/* Header */}
                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${plan.color} flex items-center justify-center`}>
                    <plan.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">{plan.name}</h3>
                  </div>
                </div>

                <p className="text-sm text-surface-200/50 mb-6">{plan.description}</p>

                {/* Price */}
                <div className="mb-6">
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl md:text-5xl font-extrabold text-white">
                      ${isAnnual ? plan.price.annual : plan.price.monthly}
                    </span>
                    <span className="text-surface-200/50 text-sm">/month</span>
                  </div>
                  {isAnnual && (
                    <p className="text-xs text-surface-200/40 mt-1">
                      Billed annually (${plan.price.annual * 12}/yr)
                    </p>
                  )}
                </div>

                {/* CTA */}
                <a
                  href="#"
                  className={`block w-full text-center py-3.5 rounded-xl font-semibold text-sm transition-all duration-300 mb-8 ${
                    plan.popular
                      ? 'btn-primary text-white relative z-10'
                      : 'glass-light text-white hover:bg-white/10'
                  }`}
                >
                  <span className="relative z-10">{plan.cta}</span>
                </a>

                {/* Features */}
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <Check className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                      <span className="text-sm text-surface-200/70">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Guarantee */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="mt-12 text-center"
        >
          <div className="inline-flex items-center gap-3 glass-light rounded-2xl px-6 py-4">
            <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <p className="text-sm text-surface-200/70">
              <strong className="text-white">30-day money-back guarantee.</strong> Try it risk-free — if it's not for you, we'll refund every penny.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
