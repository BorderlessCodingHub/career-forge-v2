import { motion } from 'framer-motion';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { Brain, Database, FlaskConical, Server, Workflow, Shield, Gauge, Code2 } from 'lucide-react';

const features = [
  {
    icon: Database,
    title: 'RAG Engineering',
    description: 'Build production-grade retrieval-augmented generation systems. Master vector databases, hybrid search, chunking strategies, and retrieval optimization.',
    color: 'from-blue-500 to-brand-500',
    tag: 'Core Module',
  },
  {
    icon: Brain,
    title: 'Fine-Tuning Mastery',
    description: 'Learn LoRA, QLoRA, and full fine-tuning techniques. Train custom models on domain-specific data with efficient GPU utilization.',
    color: 'from-purple-500 to-pink-500',
    tag: 'Core Module',
  },
  {
    icon: FlaskConical,
    title: 'LLM Evaluation',
    description: 'Implement rigorous evaluation frameworks. Master automated metrics, human evaluation protocols, and continuous quality monitoring.',
    color: 'from-emerald-400 to-teal-500',
    tag: 'Core Module',
  },
  {
    icon: Server,
    title: 'OpsLLM',
    description: 'Deploy, monitor, and scale LLM applications in production. CI/CD for ML, cost optimization, latency reduction, and observability.',
    color: 'from-amber-400 to-orange-500',
    tag: 'Core Module',
  },
  {
    icon: Workflow,
    title: 'Agent Architectures',
    description: 'Design multi-agent systems with tool use, planning, and memory. Build autonomous AI workflows that solve complex tasks.',
    color: 'from-cyan-400 to-blue-500',
    tag: 'Advanced',
  },
  {
    icon: Shield,
    title: 'Safety & Guardrails',
    description: 'Implement content filtering, prompt injection defense, bias detection, and responsible AI practices for enterprise deployments.',
    color: 'from-rose-400 to-red-500',
    tag: 'Advanced',
  },
  {
    icon: Gauge,
    title: 'Performance Optimization',
    description: 'Quantization, distillation, speculative decoding, and inference optimization. Reduce costs by 10x while maintaining quality.',
    color: 'from-violet-400 to-purple-500',
    tag: 'Advanced',
  },
  {
    icon: Code2,
    title: 'Production Patterns',
    description: 'Battle-tested design patterns for LLM apps: caching strategies, fallback chains, rate limiting, and graceful degradation.',
    color: 'from-teal-400 to-emerald-500',
    tag: 'Advanced',
  },
];

export default function Features() {
  const { ref, isVisible } = useScrollReveal();

  return (
    <section id="features" ref={ref} className="relative py-24 md:py-32 overflow-hidden">
      {/* Ambient elements */}
      <div className="ambient-orb w-[500px] h-[500px] bg-brand-600/10 top-0 right-0" style={{ animationDelay: '5s' }} />
      <div className="ambient-orb w-[400px] h-[400px] bg-accent-500/8 bottom-0 left-0" style={{ animationDelay: '12s' }} />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center max-w-3xl mx-auto mb-16 md:mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-sm font-medium text-brand-300 mb-6"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
            What You'll Master
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight"
          >
            Everything You Need to Ship{' '}
            <span className="gradient-text">Production AI</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-5 text-lg text-surface-200/70 leading-relaxed"
          >
            Our curriculum covers the full stack of modern LLM engineering — from retrieval
            systems to production deployment. Each module is project-based and mentor-guided.
          </motion.p>
        </div>

        {/* Feature grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 md:gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.15 + i * 0.08, duration: 0.6 }}
              className="group relative glass-card rounded-2xl p-6 hover:scale-[1.03] hover:shadow-2xl hover:shadow-brand-500/5 transition-all duration-500 cursor-default"
            >
              {/* Tag */}
              <span className="text-[10px] font-bold uppercase tracking-wider text-surface-200/40 mb-4 block">
                {feature.tag}
              </span>

              {/* Icon */}
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>

              {/* Content */}
              <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-surface-200/60 leading-relaxed">{feature.description}</p>

              {/* Hover accent line */}
              <div className={`absolute bottom-0 left-6 right-6 h-0.5 bg-gradient-to-r ${feature.color} opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-full`} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
