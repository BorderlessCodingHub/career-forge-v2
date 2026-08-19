import { motion } from 'framer-motion';
import { ArrowRight, Play, Star } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center pt-20 overflow-hidden noise-overlay">
      {/* Ambient orbs */}
      <div className="ambient-orb w-[600px] h-[600px] bg-brand-600/20 -top-40 -left-40" style={{ animationDelay: '0s' }} />
      <div className="ambient-orb w-[500px] h-[500px] bg-accent-500/15 top-1/3 -right-40" style={{ animationDelay: '7s' }} />
      <div className="ambient-orb w-[400px] h-[400px] bg-emerald-500/10 bottom-0 left-1/3" style={{ animationDelay: '14s' }} />

      {/* Grid pattern */}
      <div className="absolute inset-0 grid-pattern opacity-40" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left content */}
          <div>
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-light mb-8"
            >
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span className="text-sm font-medium text-surface-200">
                2025 Cohort — Limited Seats Available
              </span>
            </motion.div>

            {/* Heading */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.35 }}
              className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold tracking-tight leading-[1.08] text-white"
            >
              Become an{' '}
              <span className="gradient-text">AI/LLM</span>{' '}
              Engineer in{' '}
              <span className="relative inline-block">
                12 Weeks
                <svg className="absolute -bottom-1 left-0 w-full" viewBox="0 0 200 12" fill="none">
                  <path d="M2 8C40 3 100 1 198 6" stroke="url(#underline-grad)" strokeWidth="3" strokeLinecap="round" />
                  <defs>
                    <linearGradient id="underline-grad" x1="0" y1="0" x2="200" y2="0">
                      <stop stopColor="#748ffc" />
                      <stop offset="1" stopColor="#66d9e8" />
                    </linearGradient>
                  </defs>
                </svg>
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.5 }}
              className="mt-6 text-lg sm:text-xl text-surface-200/80 max-w-xl leading-relaxed"
            >
              Master <strong className="text-white font-semibold">RAG Engineering</strong>,{' '}
              <strong className="text-white font-semibold">Fine-Tuning</strong>,{' '}
              <strong className="text-white font-semibold">LLM Evals</strong>, and{' '}
              <strong className="text-white font-semibold">OpsLLM</strong> with hands-on projects, expert mentors, and a career-focused curriculum built for software engineers.
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.65 }}
              className="mt-10 flex flex-wrap gap-4"
            >
              <a
                href="#pricing"
                className="group inline-flex items-center gap-2 px-8 py-4 text-base font-semibold text-white rounded-2xl btn-primary relative z-10"
              >
                <span className="relative z-10 flex items-center gap-2">
                  Enroll Now
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </a>
              <a
                href="#curriculum"
                className="group inline-flex items-center gap-2 px-8 py-4 text-base font-semibold text-white rounded-2xl glass-light hover:bg-white/10 transition-all duration-300"
              >
                <Play className="w-5 h-5 text-brand-400" />
                Watch Demo
              </a>
            </motion.div>

            {/* Social proof mini */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.8 }}
              className="mt-10 flex items-center gap-6 flex-wrap"
            >
              <div className="flex -space-x-3">
                {[
                  'https://images.pexels.com/photos/14950779/pexels-photo-14950779.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=80&w=80',
                  'https://images.pexels.com/photos/8837498/pexels-photo-8837498.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=80&w=80',
                  'https://images.pexels.com/photos/38740728/pexels-photo-38740728.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=80&w=80',
                ].map((src, i) => (
                  <img
                    key={i}
                    src={src}
                    alt="Graduate"
                    className="w-10 h-10 rounded-full border-2 border-surface-950 object-cover"
                  />
                ))}
                <div className="w-10 h-10 rounded-full border-2 border-surface-950 bg-brand-600/30 flex items-center justify-center text-xs font-bold text-brand-300">
                  +2K
                </div>
              </div>
              <div>
                <div className="flex gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
                  ))}
                </div>
                <p className="text-sm text-surface-200/70 mt-0.5">
                  Trusted by <strong className="text-white">2,400+</strong> engineers
                </p>
              </div>
            </motion.div>
          </div>

          {/* Right visual - Code/Dashboard mockup */}
          <motion.div
            initial={{ opacity: 0, scale: 0.92, x: 40 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ duration: 0.9, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
            className="relative hidden lg:block"
          >
            <div className="relative">
              {/* Glow behind */}
              <div className="absolute inset-0 bg-gradient-to-br from-brand-500/20 via-accent-500/10 to-transparent rounded-3xl blur-3xl" />

              {/* Main card */}
              <div className="relative glass-card rounded-3xl p-6 glow-brand">
                {/* Terminal header */}
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-3 h-3 rounded-full bg-red-400/70" />
                  <div className="w-3 h-3 rounded-full bg-amber-400/70" />
                  <div className="w-3 h-3 rounded-full bg-emerald-400/70" />
                  <span className="ml-3 text-xs text-surface-200/50 font-mono">rag_pipeline.py</span>
                </div>

                {/* Code block */}
                <div className="code-block rounded-2xl p-5 text-sm leading-relaxed overflow-hidden">
                  <div className="space-y-1">
                    <p><span className="text-purple-400">from</span> <span className="text-blue-300">langchain</span> <span className="text-purple-400">import</span> <span className="text-emerald-300">RAGPipeline</span></p>
                    <p><span className="text-purple-400">from</span> <span className="text-blue-300">openai</span> <span className="text-purple-400">import</span> <span className="text-emerald-300">ChatCompletion</span></p>
                    <p className="text-surface-200/30">&nbsp;</p>
                    <p><span className="text-surface-200/40"># Initialize RAG with custom embeddings</span></p>
                    <p><span className="text-amber-300">pipeline</span> = <span className="text-emerald-300">RAGPipeline</span>(</p>
                    <p className="pl-6"><span className="text-blue-300">embedder</span>=<span className="text-orange-300">"text-embedding-3-large"</span>,</p>
                    <p className="pl-6"><span className="text-blue-300">retriever</span>=<span className="text-orange-300">"hybrid_search"</span>,</p>
                    <p className="pl-6"><span className="text-blue-300">reranker</span>=<span className="text-orange-300">"cohere-v3"</span>,</p>
                    <p>)</p>
                    <p className="text-surface-200/30">&nbsp;</p>
                    <p><span className="text-surface-200/40"># Fine-tuned model for domain tasks</span></p>
                    <p><span className="text-amber-300">response</span> = pipeline.<span className="text-blue-300">query</span>(</p>
                    <p className="pl-6"><span className="text-orange-300">"Explain transformer attention"</span></p>
                    <p>)</p>
                    <p className="flex items-center gap-2 mt-1">
                      <span className="text-emerald-400">✓</span>
                      <span className="text-emerald-400/80 text-xs">Pipeline ready • 12ms latency</span>
                    </p>
                  </div>
                </div>

                {/* Mini metrics bar */}
                <div className="mt-4 grid grid-cols-3 gap-3">
                  {[
                    { label: 'Accuracy', value: '94.7%', color: 'text-emerald-400' },
                    { label: 'Latency', value: '12ms', color: 'text-brand-400' },
                    { label: 'Eval Score', value: '0.96', color: 'text-accent-400' },
                  ].map((metric) => (
                    <div key={metric.label} className="glass-light rounded-xl p-3 text-center">
                      <p className={`text-lg font-bold ${metric.color}`}>{metric.value}</p>
                      <p className="text-xs text-surface-200/50">{metric.label}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Floating badge */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2, duration: 0.6 }}
                className="absolute -bottom-4 -left-4 glass-card rounded-2xl px-4 py-3 flex items-center gap-3"
              >
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Certified</p>
                  <p className="text-xs text-surface-200/60">LLM Engineer</p>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
