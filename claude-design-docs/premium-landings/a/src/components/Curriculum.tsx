import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { ChevronRight, Clock, BookOpen, Code, CheckCircle2 } from 'lucide-react';

const modules = [
  {
    week: 'Weeks 1–3',
    title: 'RAG Engineering',
    subtitle: 'Build production-ready retrieval systems',
    icon: '🔍',
    topics: [
      'Document ingestion & chunking strategies',
      'Vector databases (Pinecone, Weaviate, Qdrant)',
      'Hybrid search & semantic retrieval',
      'Re-ranking & context optimization',
      'Multi-modal RAG pipelines',
      'Project: Enterprise Knowledge Base System',
    ],
    color: 'from-blue-500 to-brand-500',
    hours: '60+ hours',
    projects: 3,
  },
  {
    week: 'Weeks 4–6',
    title: 'Fine-Tuning',
    subtitle: 'Train custom models for domain tasks',
    icon: '🧠',
    topics: [
      'Data curation & preprocessing',
      'LoRA, QLoRA & adapter methods',
      'Training infrastructure & GPU optimization',
      'Hyperparameter tuning & experiment tracking',
      'Evaluation-driven training loops',
      'Project: Domain-Specific Chat Model',
    ],
    color: 'from-purple-500 to-pink-500',
    hours: '55+ hours',
    projects: 3,
  },
  {
    week: 'Weeks 7–9',
    title: 'LLM Evaluation',
    subtitle: 'Measure and improve model quality',
    icon: '📊',
    topics: [
      'Automated eval metrics (BLEU, ROUGE, BERTScore)',
      'Custom evaluation frameworks',
      'Human evaluation protocols',
      'A/B testing for LLM outputs',
      'Continuous quality monitoring',
      'Project: Evaluation Platform & Dashboard',
    ],
    color: 'from-emerald-400 to-teal-500',
    hours: '50+ hours',
    projects: 2,
  },
  {
    week: 'Weeks 10–12',
    title: 'OpsLLM',
    subtitle: 'Deploy, scale, and monitor in production',
    icon: '🚀',
    topics: [
      'Model serving (vLLM, TGI, Triton)',
      'CI/CD for ML pipelines',
      'Cost optimization & auto-scaling',
      'Observability, logging & tracing',
      'Incident response & rollback strategies',
      'Capstone: Full Production LLM Application',
    ],
    color: 'from-amber-400 to-orange-500',
    hours: '55+ hours',
    projects: 3,
  },
];

export default function Curriculum() {
  const { ref, isVisible } = useScrollReveal();
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <section id="curriculum" ref={ref} className="relative py-24 md:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-surface-950 via-surface-900/30 to-surface-950" />
      <div className="absolute inset-0 grid-pattern opacity-20" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-sm font-medium text-accent-400 mb-6"
          >
            <BookOpen className="w-4 h-4" />
            12-Week Curriculum
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight"
          >
            A Battle-Tested{' '}
            <span className="gradient-text">Learning Path</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-5 text-lg text-surface-200/70"
          >
            Each module builds on the last, taking you from fundamentals to production mastery through hands-on projects and real-world scenarios.
          </motion.p>
        </div>

        {/* Curriculum content */}
        <div className="grid lg:grid-cols-[320px,1fr] gap-6 md:gap-8">
          {/* Module selector */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isVisible ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="space-y-3"
          >
            {modules.map((mod, i) => (
              <button
                key={i}
                onClick={() => setActiveIndex(i)}
                className={`w-full text-left p-4 rounded-2xl transition-all duration-300 group ${
                  activeIndex === i
                    ? 'glass-card shadow-lg shadow-brand-500/5 scale-[1.02]'
                    : 'hover:bg-white/[0.03]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{mod.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-surface-200/40 uppercase tracking-wider">{mod.week}</p>
                    <p className={`text-base font-bold transition-colors ${activeIndex === i ? 'text-white' : 'text-surface-200/70'}`}>
                      {mod.title}
                    </p>
                  </div>
                  <ChevronRight className={`w-5 h-5 transition-all duration-300 ${activeIndex === i ? 'text-brand-400 rotate-90' : 'text-surface-200/30'}`} />
                </div>
              </button>
            ))}
          </motion.div>

          {/* Module details */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isVisible ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={activeIndex}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.35 }}
                className="glass-card rounded-3xl p-6 md:p-8"
              >
                <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
                  <div>
                    <h3 className="text-2xl md:text-3xl font-bold text-white">{modules[activeIndex].title}</h3>
                    <p className="text-surface-200/60 mt-1">{modules[activeIndex].subtitle}</p>
                  </div>
                  <div className="flex gap-3">
                    <div className="glass-light rounded-xl px-3 py-2 flex items-center gap-2">
                      <Clock className="w-4 h-4 text-brand-400" />
                      <span className="text-sm font-medium text-surface-200/80">{modules[activeIndex].hours}</span>
                    </div>
                    <div className="glass-light rounded-xl px-3 py-2 flex items-center gap-2">
                      <Code className="w-4 h-4 text-emerald-400" />
                      <span className="text-sm font-medium text-surface-200/80">{modules[activeIndex].projects} Projects</span>
                    </div>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full h-1.5 bg-white/5 rounded-full mb-8 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 1.2, ease: 'easeOut' }}
                    className={`h-full bg-gradient-to-r ${modules[activeIndex].color} rounded-full`}
                  />
                </div>

                {/* Topics */}
                <div className="grid sm:grid-cols-2 gap-3">
                  {modules[activeIndex].topics.map((topic, i) => (
                    <motion.div
                      key={topic}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.06 }}
                      className="flex items-start gap-3 p-3 rounded-xl hover:bg-white/[0.03] transition-colors"
                    >
                      <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" />
                      <span className="text-sm text-surface-200/80 leading-relaxed">{topic}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
