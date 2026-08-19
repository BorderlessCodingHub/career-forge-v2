import { motion } from 'framer-motion';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { Star, Quote } from 'lucide-react';

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Senior ML Engineer',
    company: 'Google DeepMind',
    avatar: 'https://images.pexels.com/photos/8837498/pexels-photo-8837498.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=120&w=120',
    quote: "Career Forge transformed my career. I went from a backend engineer to leading the RAG team at DeepMind. The hands-on projects gave me real production experience that no other course could match.",
    rating: 5,
    highlight: 'Backend → ML Lead',
  },
  {
    name: 'Marcus Johnson',
    role: 'AI Platform Lead',
    company: 'Stripe',
    avatar: 'https://images.pexels.com/photos/14950779/pexels-photo-14950779.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=120&w=120',
    quote: "The OpsLLM module alone was worth the entire investment. I'm now deploying models that serve 50M+ requests/day. The fine-tuning section helped me build custom models that outperform GPT-4 on our domain tasks.",
    rating: 5,
    highlight: '$85K → $210K salary',
  },
  {
    name: 'Priya Patel',
    role: 'LLM Engineer',
    company: 'Anthropic',
    avatar: 'https://images.pexels.com/photos/5473955/pexels-photo-5473955.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=120&w=120',
    quote: "The evaluation frameworks I learned are used daily in my work at Anthropic. Career Forge doesn't just teach you tools — it teaches you how to think about AI systems at scale. Best investment I've made.",
    rating: 5,
    highlight: 'Hired within 3 weeks',
  },
  {
    name: 'David Kim',
    role: 'Staff Engineer',
    company: 'OpenAI',
    avatar: 'https://images.pexels.com/photos/38740728/pexels-photo-38740728.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=120&w=120',
    quote: "I've taken every AI course out there. Career Forge is the only one that teaches you to build production systems, not just notebooks. The mentor feedback accelerated my learning by months.",
    rating: 5,
    highlight: '3x faster learning',
  },
];

export default function Testimonials() {
  const { ref, isVisible } = useScrollReveal();

  return (
    <section id="testimonials" ref={ref} className="relative py-24 md:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-surface-950 via-surface-900/30 to-surface-950" />
      <div className="ambient-orb w-[500px] h-[500px] bg-purple-500/8 top-0 left-1/4" style={{ animationDelay: '8s' }} />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-sm font-medium text-purple-300 mb-6"
          >
            <Star className="w-4 h-4 fill-purple-300" />
            Real Results
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight"
          >
            Engineers Who{' '}
            <span className="gradient-text-warm">Leveled Up</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-5 text-lg text-surface-200/70"
          >
            Don't take our word for it — hear from graduates who transformed their careers.
          </motion.p>
        </div>

        {/* Testimonials grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 30 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.2 + i * 0.1, duration: 0.6 }}
              className="group glass-card rounded-2xl p-6 md:p-8 hover:scale-[1.01] transition-all duration-500 relative"
            >
              {/* Quote icon */}
              <Quote className="absolute top-6 right-6 w-8 h-8 text-white/5" />

              {/* Highlight tag */}
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 mb-6">
                <span className="text-xs font-semibold text-brand-300">{t.highlight}</span>
              </div>

              {/* Stars */}
              <div className="flex gap-0.5 mb-4">
                {[...Array(t.rating)].map((_, j) => (
                  <Star key={j} className="w-4 h-4 fill-amber-400 text-amber-400" />
                ))}
              </div>

              {/* Quote */}
              <p className="text-base text-surface-200/80 leading-relaxed mb-6">"{t.quote}"</p>

              {/* Author */}
              <div className="flex items-center gap-4">
                <img
                  src={t.avatar}
                  alt={t.name}
                  className="w-12 h-12 rounded-full object-cover ring-2 ring-white/10"
                />
                <div>
                  <p className="font-semibold text-white">{t.name}</p>
                  <p className="text-sm text-surface-200/50">{t.role} · {t.company}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
