import { motion } from 'framer-motion';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { useCountUp } from '../hooks/useCountUp';

const logos = [
  { name: 'Google', letter: 'G' },
  { name: 'Meta', letter: 'M' },
  { name: 'Amazon', letter: 'A' },
  { name: 'Microsoft', letter: 'MS' },
  { name: 'OpenAI', letter: 'OA' },
  { name: 'Stripe', letter: 'S' },
  { name: 'Netflix', letter: 'N' },
  { name: 'Apple', letter: 'AP' },
];

const stats = [
  { value: 2400, suffix: '+', label: 'Engineers Trained' },
  { value: 96, suffix: '%', label: 'Completion Rate' },
  { value: 45, suffix: '%', label: 'Average Salary Increase' },
  { value: 4.9, suffix: '/5', label: 'Student Rating', decimals: 1 },
];

export default function SocialProof() {
  const { ref, isVisible } = useScrollReveal();

  return (
    <section ref={ref} className="relative py-20 md:py-28 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-surface-950 via-surface-900/50 to-surface-950" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Label */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={isVisible ? { opacity: 1 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center text-sm font-medium text-surface-200/50 uppercase tracking-widest mb-10"
        >
          Trusted by engineers at top companies
        </motion.p>

        {/* Logo strip */}
        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12 mb-16 md:mb-20">
          {logos.map((logo, i) => (
            <motion.div
              key={logo.name}
              initial={{ opacity: 0, y: 20 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.1 + i * 0.06, duration: 0.5 }}
              className="group flex items-center gap-2 opacity-40 hover:opacity-80 transition-opacity duration-300 cursor-default"
            >
              <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-xs font-bold text-white/60 group-hover:text-white group-hover:bg-white/15 transition-all">
                {logo.letter}
              </div>
              <span className="text-sm font-semibold text-white/50 group-hover:text-white/80 transition-colors hidden sm:block">
                {logo.name}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
          {stats.map((stat, i) => (
            <StatCard key={stat.label} stat={stat} index={i} isVisible={isVisible} />
          ))}
        </div>
      </div>
    </section>
  );
}

function StatCard({ stat, index, isVisible }: {
  stat: { value: number; suffix: string; label: string; decimals?: number };
  index: number;
  isVisible: boolean;
}) {
  const count = useCountUp(stat.decimals ? stat.value * 10 : stat.value, isVisible);
  const displayValue = stat.decimals ? (count / 10).toFixed(1) : count;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={isVisible ? { opacity: 1, y: 0 } : {}}
      transition={{ delay: 0.3 + index * 0.1, duration: 0.6 }}
      className="glass-card rounded-2xl p-6 md:p-8 text-center group hover:scale-[1.03] transition-transform duration-300"
    >
      <p className="text-3xl md:text-4xl lg:text-5xl font-extrabold gradient-text">
        {displayValue}{stat.suffix}
      </p>
      <p className="mt-2 text-sm text-surface-200/60 font-medium">{stat.label}</p>
    </motion.div>
  );
}
