import React, { useState } from 'react';
import { ArrowRight, Terminal, Copy, Check, Play, Code, Zap, Star } from 'lucide-react';
import { PILLARS } from '../data/curriculumData';

interface HeroProps {
  onOpenApplyModal: () => void;
  onOpenSyllabusModal: () => void;
  onOpenStrategyModal: () => void;
}

export const Hero: React.FC<HeroProps> = ({
  onOpenApplyModal,
  onOpenSyllabusModal,
  onOpenStrategyModal
}) => {
  const [activeTabId, setActiveTabId] = useState<'rag' | 'finetuner' | 'evals' | 'opsllm'>('rag');
  const [copied, setCopied] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const activePillar = PILLARS.find(p => p.id === activeTabId) || PILLARS[0];

  const handleCopy = () => {
    navigator.clipboard.writeText(activePillar.codeSnippet.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRunCode = () => {
    setIsRunning(true);
    setLogs(['[SYS] Initializing local test runner...', '[SYS] Loading quantized weights & vector store configuration...']);
    setTimeout(() => {
      setLogs(prev => [...prev, `[EXEC] Running ${activePillar.codeSnippet.filename}...`]);
    }, 600);
    setTimeout(() => {
      setLogs(prev => [...prev, activePillar.codeSnippet.output]);
      setIsRunning(false);
    }, 1400);
  };

  return (
    <section className="relative pt-8 pb-20 md:pt-14 md:pb-32 overflow-hidden bg-slate-950">
      {/* Dynamic Background Effects */}
      <div className="absolute inset-0 bg-dot-grid opacity-30 pointer-events-none"></div>
      
      {/* Radial Glow Orbs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-orange-600/15 via-indigo-600/20 to-purple-600/15 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute top-10 right-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Top Cohort Announcement Badge */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/90 border border-orange-500/30 shadow-lg shadow-orange-500/10 text-xs sm:text-sm backdrop-blur-md">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
            </span>
            <span className="font-semibold text-slate-200">
              COHORT 12 ENROLLMENT OPEN
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-orange-400 font-mono font-bold">
              8 SEATS REMAINING
            </span>
            <span className="hidden sm:inline-block bg-orange-500/20 text-orange-300 px-2 py-0.5 rounded text-[11px] font-bold">
              SAVE $500
            </span>
          </div>
        </div>

        {/* Hero Main Headline & Subheadline */}
        <div className="text-center max-w-4xl mx-auto mb-10">
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-[1.15] mb-6">
            From Software Engineer to{' '}
            <span className="gradient-text-hero underline decoration-orange-500/40 underline-offset-8">
              Elite AI Engineer
            </span>
          </h1>
          
          <p className="text-base sm:text-xl text-slate-300 leading-relaxed max-w-3xl mx-auto font-normal">
            Master the 4 non-negotiable pillars of production AI engineering:{' '}
            <strong className="text-orange-400 font-semibold">RAG Engineering</strong>,{' '}
            <strong className="text-purple-400 font-semibold">Fine-Tuning</strong>,{' '}
            <strong className="text-cyan-400 font-semibold">LLM Evals</strong>, and{' '}
            <strong className="text-emerald-400 font-semibold">OpsLLM</strong>. Architect scale systems, command top 1% compensation.
          </p>
        </div>

        {/* Primary CTA Button Group */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
          <button
            onClick={onOpenApplyModal}
            className="w-full sm:w-auto relative group px-8 py-4 rounded-xl text-base font-extrabold text-white shimmer-button shadow-xl shadow-orange-500/20 hover:shadow-orange-500/40 transform hover:-translate-y-0.5 transition-all flex items-center justify-center gap-3 cursor-pointer"
          >
            <span>Apply For Cohort 12 ($500 Off)</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>

          <button
            onClick={onOpenSyllabusModal}
            className="w-full sm:w-auto px-6 py-4 rounded-xl text-sm font-bold text-slate-200 bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 hover:border-slate-600 transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg"
          >
            <Code className="w-4 h-4 text-slate-400" />
            <span>Download 2026 AI Curriculum</span>
          </button>

          <button
            onClick={onOpenStrategyModal}
            className="w-full sm:w-auto px-5 py-4 rounded-xl text-xs font-semibold text-slate-400 hover:text-white transition-colors cursor-pointer text-center"
          >
            Book 1-on-1 Strategy Call →
          </button>
        </div>

        {/* Micro-Trust Highlights Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 max-w-4xl mx-auto mb-14">
          <div className="glass-panel p-3.5 rounded-xl text-center border border-slate-800">
            <div className="text-xl sm:text-2xl font-extrabold text-orange-400 font-mono">+$84,500</div>
            <div className="text-xs text-slate-400 font-medium mt-0.5">Avg Salary Increase</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl text-center border border-slate-800">
            <div className="text-xl sm:text-2xl font-extrabold text-indigo-400 font-mono">94.8%</div>
            <div className="text-xs text-slate-400 font-medium mt-0.5">Placement in 90 Days</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl text-center border border-slate-800">
            <div className="text-xl sm:text-2xl font-extrabold text-cyan-400 font-mono">$500 Credits</div>
            <div className="text-xs text-slate-400 font-medium mt-0.5">Nvidia A100/H100 Included</div>
          </div>
          <div className="glass-panel p-3.5 rounded-xl text-center border border-slate-800">
            <div className="flex items-center justify-center gap-1 text-xl sm:text-2xl font-extrabold text-yellow-400 font-mono">
              4.96 <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            </div>
            <div className="text-xs text-slate-400 font-medium mt-0.5">640+ Alumni Ratings</div>
          </div>
        </div>

        {/* Interactive Code Playground / Terminal Showcase */}
        <div className="max-w-5xl mx-auto">
          <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800 shadow-2xl relative">
            
            {/* Top Bar with Tab Switches */}
            <div className="bg-slate-900/90 border-b border-slate-800 px-4 py-3 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <span className="text-xs font-mono text-slate-400 ml-2 flex items-center gap-1">
                  <Terminal className="w-3.5 h-3.5 text-slate-400" />
                  career-forge-ai-stack // {activePillar.codeSnippet.filename}
                </span>
              </div>

              {/* Pillar Tabs */}
              <div className="flex flex-wrap items-center gap-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800">
                {PILLARS.map((p) => {
                  const isActive = p.id === activeTabId;
                  return (
                    <button
                      key={p.id}
                      onClick={() => {
                        setActiveTabId(p.id);
                        setLogs([]);
                      }}
                      className={`text-xs font-semibold px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 cursor-pointer ${
                        isActive
                          ? 'bg-gradient-to-r from-slate-800 to-slate-900 text-white shadow border border-slate-700 font-bold'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <span className={isActive ? p.accentColor : 'text-slate-500'}>
                        {p.id === 'rag' && '⚡ RAG'}
                        {p.id === 'finetuner' && '🦥 Fine-Tuning'}
                        {p.id === 'evals' && '🛡️ Evals'}
                        {p.id === 'opsllm' && '🚀 OpsLLM'}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Pillar Meta Banner */}
            <div className="bg-slate-900/50 px-5 py-3 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-xs">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded font-bold font-mono text-[11px] bg-slate-800 border ${activePillar.borderColor} ${activePillar.accentColor}`}>
                  {activePillar.badge}
                </span>
                <span className="text-slate-300 font-medium hidden sm:inline">
                  {activePillar.subtitle}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleRunCode}
                  disabled={isRunning}
                  className="px-3 py-1 bg-emerald-600/90 hover:bg-emerald-500 text-white font-mono font-bold text-[11px] rounded flex items-center gap-1 shadow cursor-pointer transition-colors"
                >
                  <Play className={`w-3 h-3 ${isRunning ? 'animate-spin' : ''}`} />
                  {isRunning ? 'Executing...' : 'Run Simulation'}
                </button>
                <button
                  onClick={handleCopy}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-mono text-[11px] rounded flex items-center gap-1 border border-slate-700 transition-colors cursor-pointer"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>

            {/* Code Body */}
            <div className="p-5 bg-[#0d1117] overflow-x-auto text-xs sm:text-sm font-mono text-slate-300 leading-relaxed min-h-[260px] max-h-[380px] scrollbar-thin">
              <pre className="selection:bg-indigo-500/30">
                <code>{activePillar.codeSnippet.code}</code>
              </pre>

              {/* Interactive Execution Output Console */}
              {(logs.length > 0 || isRunning) && (
                <div className="mt-4 pt-4 border-t border-slate-800 font-mono text-xs">
                  <div className="text-slate-500 font-semibold mb-1 flex items-center gap-1">
                    <Zap className="w-3 h-3 text-amber-400" /> Console Output:
                  </div>
                  {logs.map((log, i) => (
                    <div
                      key={i}
                      className={
                        log.startsWith('✓')
                          ? 'text-emerald-400 font-bold bg-emerald-950/40 p-2 rounded border border-emerald-500/30 mt-1'
                          : 'text-slate-400 py-0.5'
                      }
                    >
                      {log}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Code Footer Tech Badges */}
            <div className="bg-slate-900/90 px-5 py-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
              <span className="text-slate-400 font-mono">
                Tech Stack Mastered:
              </span>
              <div className="flex flex-wrap items-center gap-2">
                {activePillar.techStack.map((tech, idx) => (
                  <span
                    key={idx}
                    className="bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 px-2.5 py-1 rounded-md font-mono text-[11px] flex items-center gap-1 transition-colors"
                  >
                    <span>{tech.logo}</span>
                    <span>{tech.name}</span>
                  </span>
                ))}
              </div>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
};
