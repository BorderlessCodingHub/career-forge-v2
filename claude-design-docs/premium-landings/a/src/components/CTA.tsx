import { motion } from 'framer-motion';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { ArrowRight, Sparkles } from 'lucide-react';

export default function CTA() {
  const { ref, isVisible } = useScrollReveal();

  return (
    <section ref={ref} className="relative py-24 md:py-32 overflow-hidden">
      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isVisible ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="relative overflow-hidden rounded-[2rem] md:rounded-[2.5rem]"
        >
          {/* Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-brand-700 via-brand-600 to-accent-600" />
          <div className="absolute inset-0 grid-pattern opacity-10" />

          {/* Decorative orbs */}
          <div className="absolute -top-20 -right-20 w-[300px] h-[300px] bg-white/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-[300px] h-[300px] bg-accent-500/20 rounded-full blur-3xl" />

          {/* Content */}
          <div className="relative z-10 p-8 md:p-12 lg:p-16 text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={isVisible ? { opacity: 1, scale: 1 } : {}}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 mb-8"
            >
              <Sparkles className="w-4 h-4 text-amber-300" />
              <span className="text-sm font-semibold text-white/90">Next Cohort Starts January 2026</span>
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-white tracking-tight leading-tight"
            >
              Ready to Forge Your
              <br />
              AI Engineering Career?
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="mt-6 text-lg md:text-xl text-white/70 max-w-2xl mx-auto"
            >
              Join 2,400+ software engineers who've already made the transition. 
              Limited seats available for the upcoming cohort.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <a
                href="#pricing"
                className="group inline-flex items-center gap-2 px-10 py-4 text-base font-bold text-brand-700 bg-white rounded-2xl hover:bg-white/90 hover:scale-105 hover:shadow-2xl hover:shadow-white/20 transition-all duration-300"
              >
                Enroll Now — Start Building
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </a>
              <a
                href="#curriculum"
                className="inline-flex items-center gap-2 px-8 py-4 text-base font-semibold text-white rounded-2xl border border-white/20 hover:bg-white/10 transition-all duration-300"
              >
                View Full Curriculum
              </a>
            </motion.div>

            {/* Trust signals */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={isVisible ? { opacity: 1 } : {}}
              transition={{ delay: 0.7, duration: 0.6 }}
              className="mt-10 flex flex-wrap items-center justify-center gap-6 text-sm text-white/50"
            >
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                30-day money-back
              </span>
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Lifetime access
              </span>
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Job guarantee
              </span>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
