"use client";

import { useEffect, useState } from "react";
import { useLocale } from "next-intl";
import { Sparkles, CheckCircle, Cpu, Database, Shield, Zap } from 'lucide-react';
import { useWelcomeText } from "./useWelcomeText";

export function InteractiveSandbox() {
  const locale = useLocale();
  const { text } = useWelcomeText();
  const [activeSandbox, setActiveSandbox] = useState<'rag' | 'finetune' | 'evals' | 'opsllm'>('rag');

  // RAG Simulator state
  const [ragMode, setRagMode] = useState<'naive' | 'hybrid'>('hybrid');
  const defaultQuery = text("playground.defaultQuery");
  const [queryText, setQueryText] = useState(defaultQuery);

  // Fine-tuning state
  const [loraRank, setLoraRank] = useState(32);
  const [loraAlpha, setLoraAlpha] = useState(64);
  const [quantization, setQuantization] = useState<'4bit' | '8bit' | 'fp16'>('4bit');

  // Evals state
  const defaultEval = text("playground.defaultEval");
  const [evalPrompt, setEvalPrompt] = useState(defaultEval);
  const [evalRunning, setEvalRunning] = useState(false);
  const [evalResults, setEvalRunningResults] = useState<{
    faithfulness: number;
    hallucination: number;
    toxicity: number;
    passed: boolean;
  } | null>(null);

  // OpsLLM state
  const [concurrentRps, setConcurrentRps] = useState(250);
  const [engineType, setEngineType] = useState<'vllm' | 'pytorch'>('vllm');

  useEffect(() => {
    setQueryText(defaultQuery);
    setEvalPrompt(defaultEval);
  }, [locale, defaultQuery, defaultEval]);

  // Calculations for Fine-tuning
  const baseVram = quantization === '4bit' ? 12 : quantization === '8bit' ? 22 : 48;
  const loraVram = (loraRank / 32) * 2.2;
  const totalVram = (baseVram + loraVram).toFixed(1);
  const trainingSpeed = quantization === '4bit' ? text("playground.speed4") : quantization === '8bit' ? text("playground.speed8") : text("playground.speed16");

  // Calculations for OpsLLM
  const ttft = engineType === 'vllm' ? Math.round(28 + (concurrentRps / 50)) : Math.round(450 + (concurrentRps * 1.8));
  const throughput = engineType === 'vllm' ? Math.round(1450 * (concurrentRps / 200)) : Math.round(180 * (concurrentRps / 200));
  const memoryUtilization = engineType === 'vllm' ? Math.min(96, Math.round(60 + (concurrentRps / 15))) : Math.min(100, Math.round(85 + (concurrentRps / 5)));

  const handleRunEval = () => {
    setEvalRunning(true);
    setTimeout(() => {
      setEvalRunningResults({
        faithfulness: 0.96,
        hallucination: 0.02,
        toxicity: 0.00,
        passed: true
      });
      setEvalRunning(false);
    }, 800);
  };

  return (
    <section id="sandbox" className="py-24 bg-slate-950 border-t border-slate-900 relative overflow-hidden">
      
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-cyan-600/10 rounded-full blur-[140px] pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            {text("playground.eyebrow")}
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            {text("playground.titleBefore")} <span className="gradient-text-cyan">{text("playground.titleAccent")}</span>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base">
            {text("playground.lead")}
          </p>
        </div>

        {/* Sandbox Navigation Tabs */}
        <div className="flex flex-wrap justify-center gap-2 sm:gap-3 mb-8">
          {[
            { id: 'rag', label: text("playground.tabRag"), icon: Database, color: 'text-orange-400', border: 'border-orange-500/40' },
            { id: 'finetune', label: text("playground.tabTune"), icon: Cpu, color: 'text-purple-400', border: 'border-purple-500/40' },
            { id: 'evals', label: text("playground.tabEvals"), icon: Shield, color: 'text-cyan-400', border: 'border-cyan-500/40' },
            { id: 'opsllm', label: text("playground.tabOps"), icon: Zap, color: 'text-emerald-400', border: 'border-emerald-500/40' }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSandbox === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSandbox(tab.id as any)}
                className={`px-4 py-2.5 rounded-xl font-mono text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
                  isActive
                    ? `bg-slate-900 text-white shadow-lg border ${tab.border} ring-1 ring-slate-700`
                    : 'bg-slate-950/80 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                <Icon className={`w-4 h-4 ${tab.color}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Sandbox Screen Container */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 bg-slate-900/90 shadow-2xl max-w-5xl mx-auto">
          
          {/* 1. RAG SIMULATOR */}
          {activeSandbox === 'rag' && (
            <div className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Database className="w-5 h-5 text-orange-400" />
                    {text("playground.ragTitle")}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {text("playground.ragLead")}
                  </p>
                </div>

                <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
                  <button
                    onClick={() => setRagMode('naive')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                      ragMode === 'naive' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'text-slate-400'
                    }`}
                  >
                    {text("playground.naive")}
                  </button>
                  <button
                    onClick={() => setRagMode('hybrid')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                      ragMode === 'hybrid' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : 'text-slate-400'
                    }`}
                  >
                    {text("playground.hybrid")}
                  </button>
                </div>
              </div>

              {/* Input Query */}
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-2 font-bold">
                  {text("playground.queryLabel")}
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={queryText}
                    onChange={(e) => setQueryText(e.target.value)}
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-orange-500"
                  />
                </div>
              </div>

              {/* Simulation Result */}
              <div className="grid sm:grid-cols-3 gap-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-1">{text("playground.precision")}</div>
                  <div className={`text-2xl font-extrabold font-mono ${ragMode === 'hybrid' ? 'text-emerald-400' : 'text-red-400'}`}>
                    {ragMode === 'hybrid' ? '98.4%' : '61.2%'}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {ragMode === 'hybrid' ? text("playground.precisionGood") : text("playground.precisionBad")}
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-1">{text("playground.latency")}</div>
                  <div className="text-2xl font-extrabold font-mono text-cyan-400">
                    {ragMode === 'hybrid' ? '184 ms' : '310 ms'}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {ragMode === 'hybrid' ? text("playground.latencyGood") : text("playground.latencyBad")}
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-1">{text("playground.hallucination")}</div>
                  <div className={`text-2xl font-extrabold font-mono ${ragMode === 'hybrid' ? 'text-emerald-400' : 'text-orange-400'}`}>
                    {ragMode === 'hybrid' ? '0.01 %' : '18.4 %'}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {ragMode === 'hybrid' ? text("playground.hallucinationGood") : text("playground.hallucinationBad")}
                  </div>
                </div>
              </div>

              {/* Code/Pipeline Visual */}
              <div className="bg-[#0b0f19] p-4 rounded-xl border border-slate-800 text-xs font-mono text-slate-300">
                <div className="text-slate-500 font-bold mb-2">{text("playground.retrieved")}</div>
                {ragMode === 'hybrid' ? (
                  <div className="space-y-1.5 text-emerald-300/90">
                    <div>[Match 1] SEC 10-K Filing p.42: "Q3 Cloud profit margin stood at 28.1% on $420M revenue..." (Score: 0.984)</div>
                    <div>[Match 2] Earnings Call Transcript: "Cloud margins expanded 140 bps year-over-year..." (Score: 0.941)</div>
                  </div>
                ) : (
                  <div className="space-y-1.5 text-red-300/80">
                    <div>[Match 1] General Corporate Overview: "Acme operates cloud platforms across NA..." (Score: 0.612)</div>
                    <div>[Match 2] Unrelated Q1 SEC Footnote: "Margins subject to foreign exchange fluctuations..." (Score: 0.580)</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 2. FINE-TUNING SIMULATOR */}
          {activeSandbox === 'finetune' && (
            <div className="space-y-6">
              <div className="pb-4 border-b border-slate-800">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-purple-400" />
                  {text("playground.tuneTitle")}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  {text("playground.tuneLead")}
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-6">
                
                {/* Sliders */}
                <div className="space-y-4 md:col-span-2 bg-slate-950 p-5 rounded-2xl border border-slate-800">
                  <div>
                    <div className="flex justify-between text-xs font-mono mb-1">
                      <span className="text-slate-300 font-bold">{text("playground.loraRank")}</span>
                      <span className="text-purple-400 font-bold font-mono">r = {loraRank}</span>
                    </div>
                    <input
                      type="range"
                      min="8"
                      max="128"
                      step="8"
                      value={loraRank}
                      onChange={(e) => setLoraRank(Number(e.target.value))}
                      className="w-full accent-purple-500 cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-mono mb-1">
                      <span className="text-slate-300 font-bold">{text("playground.loraAlpha")}</span>
                      <span className="text-indigo-400 font-bold font-mono">α = {loraAlpha}</span>
                    </div>
                    <input
                      type="range"
                      min="16"
                      max="256"
                      step="16"
                      value={loraAlpha}
                      onChange={(e) => setLoraAlpha(Number(e.target.value))}
                      className="w-full accent-indigo-500 cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="text-xs font-mono text-slate-300 font-bold mb-2">
                      {text("playground.quant")}
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      {(['4bit', '8bit', 'fp16'] as const).map((q) => (
                        <button
                          key={q}
                          onClick={() => setQuantization(q)}
                          className={`py-2 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                            quantization === q
                              ? 'bg-purple-600 text-white shadow border border-purple-400'
                              : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
                          }`}
                        >
                          {q === '4bit' ? text("playground.q4") : q === '8bit' ? text("playground.q8") : text("playground.fp16")}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Live Calculated Stats */}
                <div className="bg-slate-950 p-5 rounded-2xl border border-purple-500/30 flex flex-col justify-between">
                  <div>
                    <div className="text-xs font-mono text-purple-400 font-bold uppercase tracking-wider mb-2">
                      {text("playground.vram")}
                    </div>
                    <div className="text-4xl font-extrabold font-mono text-white mb-1">
                      {totalVram} <span className="text-lg text-purple-400">GB</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      {text("playground.vramFit")}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-slate-800 space-y-2 text-xs font-mono">
                    <div className="flex justify-between">
                      <span className="text-slate-400">{text("playground.throughput")}</span>
                      <span className="text-emerald-400 font-bold">{trainingSpeed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">{text("playground.adapter")}</span>
                      <span className="text-purple-300 font-bold">{text("playground.million", { count: (loraRank * 1.8).toFixed(1) })}</span>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* 3. EVALS SIMULATOR */}
          {activeSandbox === 'evals' && (
            <div className="space-y-6">
              <div className="pb-4 border-b border-slate-800">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Shield className="w-5 h-5 text-cyan-400" />
                  {text("playground.evalsTitle")}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  {text("playground.evalsLead")}
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={evalPrompt}
                    onChange={(e) => setEvalPrompt(e.target.value)}
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                  />
                  <button
                    onClick={handleRunEval}
                    disabled={evalRunning}
                    className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-mono font-bold text-xs rounded-xl shadow cursor-pointer transition-colors"
                  >
                    {evalRunning ? text("playground.running") : text("playground.execute")}
                  </button>
                </div>

                {/* Assertion Results */}
                {evalResults ? (
                  <div className="grid sm:grid-cols-3 gap-3 pt-2">
                    <div className="bg-slate-950 p-3.5 rounded-xl border border-emerald-500/30">
                      <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-1">
                        <span>{text("playground.faithfulness")}</span>
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      </div>
                      <div className="text-2xl font-extrabold font-mono text-emerald-400">
                        {evalResults.faithfulness}
                      </div>
                      <div className="text-[10px] text-slate-500 mt-1">{text("playground.faithfulnessThreshold")}</div>
                    </div>

                    <div className="bg-slate-950 p-3.5 rounded-xl border border-emerald-500/30">
                      <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-1">
                        <span>{text("playground.hallucinationRate")}</span>
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      </div>
                      <div className="text-2xl font-extrabold font-mono text-emerald-400">
                        {evalResults.hallucination}
                      </div>
                      <div className="text-[10px] text-slate-500 mt-1">{text("playground.hallucinationThreshold")}</div>
                    </div>

                    <div className="bg-slate-950 p-3.5 rounded-xl border border-emerald-500/30">
                      <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-1">
                        <span>{text("playground.toxicity")}</span>
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      </div>
                      <div className="text-2xl font-extrabold font-mono text-emerald-400">
                        {evalResults.toxicity}
                      </div>
                      <div className="text-[10px] text-slate-500 mt-1">{text("playground.toxicityThreshold")}</div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-950 p-6 rounded-xl text-center text-xs font-mono text-slate-500 border border-slate-800">
                    {text("playground.evalsEmpty")}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 4. OPSLLM SIMULATOR */}
          {activeSandbox === 'opsllm' && (
            <div className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Zap className="w-5 h-5 text-emerald-400" />
                    {text("playground.opsTitle")}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {text("playground.opsLead")}
                  </p>
                </div>

                <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
                  <button
                    onClick={() => setEngineType('pytorch')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                      engineType === 'pytorch' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'text-slate-400'
                    }`}
                  >
                    {text("playground.hf")}
                  </button>
                  <button
                    onClick={() => setEngineType('vllm')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                      engineType === 'vllm' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-400'
                    }`}
                  >
                    {text("playground.vllm")}
                  </button>
                </div>
              </div>

              {/* Slider for RPS */}
              <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800">
                <div className="flex justify-between text-xs font-mono mb-2">
                  <span className="text-slate-300 font-bold">{text("playground.load")}</span>
                  <span className="text-emerald-400 font-bold font-mono text-sm">{concurrentRps} RPS</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="1000"
                  step="20"
                  value={concurrentRps}
                  onChange={(e) => setConcurrentRps(Number(e.target.value))}
                  className="w-full accent-emerald-500 cursor-pointer"
                />
              </div>

              {/* Calculated Metrics */}
              <div className="grid sm:grid-cols-3 gap-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-1">{text("playground.ttft")}</div>
                  <div className={`text-2xl font-extrabold font-mono ${ttft < 100 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {ttft} ms
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {engineType === 'vllm' ? text("playground.ttftGood") : text("playground.ttftBad")}
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-1">{text("playground.output")}</div>
                  <div className="text-2xl font-extrabold font-mono text-cyan-400">
                    {throughput} tok/sec
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {engineType === 'vllm' ? text("playground.outputGood") : text("playground.outputBad")}
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-1">{text("playground.kv")}</div>
                  <div className="text-2xl font-extrabold font-mono text-purple-400">
                    {memoryUtilization} %
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {engineType === 'vllm' ? text("playground.kvGood") : text("playground.kvBad")}
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

      </div>
    </section>
  );
};
