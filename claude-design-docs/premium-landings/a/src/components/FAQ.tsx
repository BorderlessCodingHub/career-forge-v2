import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { Plus, Minus } from 'lucide-react';

const faqs = [
  {
    question: 'Do I need machine learning experience to enroll?',
    answer: 'No ML experience required! Career Forge is specifically designed for software engineers transitioning into AI/LLM engineering. If you can write production code in Python and understand basic APIs, you have everything you need to succeed. We teach the ML fundamentals as we go.',
  },
  {
    question: 'How much time should I commit per week?',
    answer: 'We recommend 15–20 hours per week for the best experience. This includes video lectures (~5 hrs), project work (~8 hrs), and optional mentor sessions and community activities. Many students balance this alongside a full-time job.',
  },
  {
    question: 'What makes this different from free YouTube content?',
    answer: "Three things: structured curriculum, production focus, and mentorship. Our curriculum is designed as a progressive learning path — not random tutorials. Every project mirrors real production systems, not toy examples. And you get feedback from engineers at OpenAI, Google, and Anthropic who've built these systems at scale.",
  },
  {
    question: 'What programming languages and tools are used?',
    answer: 'Primarily Python, with production tooling including LangChain, LlamaIndex, Hugging Face, vLLM, PyTorch, Weights & Biases, and major cloud platforms (AWS, GCP). You\'ll also work with vector databases like Pinecone, Weaviate, and Qdrant.',
  },
  {
    question: 'Is the job guarantee real?',
    answer: 'Yes. Our Pro plan includes a job guarantee: if you complete the full program, pass the final assessment, and don\'t land a qualifying AI/ML engineering role within 6 months, we refund your tuition in full. We define "qualifying role" as any position with AI/ML in the title at a company with 50+ employees.',
  },
  {
    question: 'Can I get my company to pay for this?',
    answer: 'Absolutely! Over 60% of our students get employer sponsorship. We provide a ready-to-send justification letter, ROI calculator, and W-9/invoice for your L&D team. Our Enterprise plan also offers bulk pricing and team dashboards.',
  },
  {
    question: 'What kind of support do I get?',
    answer: 'Self-Paced students get community support via our Discord with 2,400+ members. Pro students additionally get weekly 1-on-1 mentorship, code reviews from industry experts, career coaching, and priority email support with <4 hour response time.',
  },
  {
    question: 'Do I keep access after the 12 weeks?',
    answer: 'Yes! All students get lifetime access to course materials, including all future updates. As the LLM landscape evolves, your curriculum evolves with it. Pro and Enterprise students also retain lifetime community access.',
  },
];

export default function FAQ() {
  const { ref, isVisible } = useScrollReveal();
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section id="faq" ref={ref} className="relative py-24 md:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-surface-950 via-surface-900/20 to-surface-950" />

      <div className="relative z-10 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-sm font-medium text-surface-200/70 mb-6"
          >
            💬 FAQ
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight"
          >
            Common{' '}
            <span className="gradient-text">Questions</span>
          </motion.h2>
        </div>

        {/* FAQ list */}
        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.15 + i * 0.05, duration: 0.5 }}
            >
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full text-left glass-card rounded-2xl p-5 md:p-6 group hover:bg-white/[0.04] transition-all duration-300"
                aria-expanded={openIndex === i}
              >
                <div className="flex items-start justify-between gap-4">
                  <h3 className="text-base md:text-lg font-semibold text-white group-hover:text-brand-300 transition-colors pr-4">
                    {faq.question}
                  </h3>
                  <div className="shrink-0 w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center group-hover:bg-brand-500/20 transition-colors">
                    {openIndex === i ? (
                      <Minus className="w-4 h-4 text-brand-400" />
                    ) : (
                      <Plus className="w-4 h-4 text-surface-200/50" />
                    )}
                  </div>
                </div>

                <AnimatePresence>
                  {openIndex === i && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                      className="overflow-hidden"
                    >
                      <p className="mt-4 text-sm md:text-base text-surface-200/60 leading-relaxed">
                        {faq.answer}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
