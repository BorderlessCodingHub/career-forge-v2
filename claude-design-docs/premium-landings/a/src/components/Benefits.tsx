import { motion } from 'framer-motion';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { Rocket, Users, Award, Laptop, HeartHandshake, TrendingUp } from 'lucide-react';

const benefits = [
  {
    icon: Rocket,
    title: 'Career Acceleration',
    description: 'Average 45% salary increase within 6 months. Our graduates land roles at top AI labs and tech companies.',
    stat: '45%',
    statLabel: 'Avg salary bump',
  },
  {
    icon: Users,
    title: 'Expert Mentorship',
    description: 'Weekly 1-on-1 sessions with engineers from OpenAI, Google DeepMind, and Anthropic. Real feedback, real growth.',
    stat: '1:8',
    statLabel: 'Mentor ratio',
  },
  {
    icon: Laptop,
    title: 'Hands-On Projects',
    description: '12+ production-grade projects that become your portfolio. Build systems that handle millions of queries per day.',
    stat: '12+',
    statLabel: 'Portfolio projects',
  },
  {
    icon: Award,
    title: 'Industry Certification',
    description: 'Earn a recognized LLM Engineering certification. Verified by industry experts and accepted by 500+ companies.',
    stat: '500+',
    statLabel: 'Partner companies',
  },
  {
    icon: HeartHandshake,
    title: 'Community Access',
    description: 'Join a private network of 2,400+ AI engineers. Lifetime access to alumni channels, job boards, and events.',
    stat: '2.4K+',
    statLabel: 'Active members',
  },
  {
    icon: TrendingUp,
    title: 'Job Guarantee',
    description: "Land a qualifying role within 6 months or get a full refund. We're that confident in our program.",
    stat: '100%',
    statLabel: 'Money-back promise',
  },
];

export default function Benefits() {
  const { ref, isVisible } = useScrollReveal();

  return (
    <section id="benefits" ref={ref} className="relative py-24 md:py-32 overflow-hidden">
      <div className="ambient-orb w-[500px] h-[500px] bg-emerald-500/8 top-1/4 -right-40" style={{ animationDelay: '3s' }} />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-sm font-medium text-emerald-400 mb-6"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Why Career Forge
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight"
          >
            Built for Engineers Who{' '}
            <span className="gradient-text">Ship</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-5 text-lg text-surface-200/70"
          >
            We don't just teach theory — we build the bridge from software engineer to AI/LLM engineer with real projects, expert mentors, and career support.
          </motion.p>
        </div>

        {/* Benefits grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {benefits.map((benefit, i) => (
            <motion.div
              key={benefit.title}
              initial={{ opacity: 0, y: 30 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.15 + i * 0.08, duration: 0.6 }}
              className="group relative glass-card rounded-2xl p-6 md:p-8 hover:scale-[1.02] transition-all duration-500"
            >
              {/* Stat badge */}
              <div className="absolute top-6 right-6">
                <div className="text-right">
                  <p className="text-2xl font-extrabold gradient-text">{benefit.stat}</p>
                  <p className="text-[10px] uppercase tracking-wider text-surface-200/40 font-medium">{benefit.statLabel}</p>
                </div>
              </div>

              {/* Icon */}
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-500/20 to-accent-500/20 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                <benefit.icon className="w-6 h-6 text-brand-400" />
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold text-white mb-3">{benefit.title}</h3>
              <p className="text-sm text-surface-200/60 leading-relaxed">{benefit.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
