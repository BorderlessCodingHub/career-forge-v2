"use client";

import { useState } from "react";
import Link from "next/link";
import { PILLARS } from './data/curriculumData';
import { Database, Cpu, ShieldCheck, Server, ArrowRight, Layers, Sparkles, BookOpen } from 'lucide-react';
import { useWelcomeText } from "./useWelcomeText";

type FlowStep = { title: string; description: string };

export function PillarsOverview() {
  const { text, list } = useWelcomeText();
  const [selectedPillarId, setSelectedPillarId] = useState<'rag' | 'finetuner' | 'evals' | 'opsllm'>('rag');

  const activePillar = PILLARS.find(p => p.id === selectedPillarId) || PILLARS[0];

  const getPillarIcon = (id: string) => {
    switch (id) {
      case 'rag': return <Database className="w-6 h-6 text-orange-400" />;
      case 'finetuner': return <Cpu className="w-6 h-6 text-purple-400" />;
      case 'evals': return <ShieldCheck className="w-6 h-6 text-cyan-400" />;
      case 'opsllm': return <Server className="w-6 h-6 text-emerald-400" />;
      default: return <Layers className="w-6 h-6 text-indigo-400" />;
    }
  };

  return (
    <section id="pillars" className="py-24 bg-slate-950 relative border-t border-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-4">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            {text("mastery.eyebrow")}
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            {text("mastery.titleBefore")} <span className="gradient-text-hero">{text("mastery.titleAccent")}</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            {text("mastery.lead")}
          </p>
        </div>

        {/* 4 Pillar Switcher Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-12">
          {PILLARS.map((p) => {
            const isActive = p.id === selectedPillarId;
            return (
              <button
                key={p.id}
                onClick={() => setSelectedPillarId(p.id)}
                className={`p-4 sm:p-5 rounded-2xl text-left transition-all cursor-pointer relative overflow-hidden border ${
                  isActive
                    ? `bg-slate-900 shadow-xl ${p.borderColor} ring-1 ring-slate-700`
                    : 'glass-panel hover:bg-slate-900/60 border-slate-800/80 opacity-75 hover:opacity-100'
                }`}
              >
                {isActive && (
                  <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${p.accentColor.includes('orange') ? 'from-orange-500 to-amber-500' : p.accentColor.includes('purple') ? 'from-purple-500 to-indigo-500' : p.accentColor.includes('cyan') ? 'from-cyan-500 to-blue-500' : 'from-emerald-500 to-teal-500'}`}></div>
                )}
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2.5 rounded-xl bg-slate-950 border border-slate-800`}>
                    {getPillarIcon(p.id)}
                  </div>
                  <span className="font-mono text-[11px] font-extrabold text-slate-500">
                    0{PILLARS.findIndex(item => item.id === p.id) + 1}
                  </span>
                </div>
                <h3 className="text-base sm:text-lg font-bold text-white mb-1">
                  {p.title}
                </h3>
                <p className={`text-xs ${isActive ? p.accentColor : 'text-slate-400'} font-medium line-clamp-1`}>
                  {text(`track.${p.id}.badge`)}
                </p>
              </button>
            );
          })}
        </div>

        {/* Active Pillar Expanded Showcase */}
        <div className="glass-panel rounded-3xl p-6 sm:p-10 border border-slate-800 bg-slate-900/80 shadow-2xl relative overflow-hidden">
          
          <div className="grid lg:grid-cols-12 gap-8 items-start">
            
            {/* Left Column: Skills & Architecture Flow */}
            <div className="lg:col-span-7 space-y-8">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 text-xs font-mono font-bold text-slate-300 border border-slate-700 mb-3">
                  {text("mastery.blueprint")}
                </div>
                <h3 className="text-2xl sm:text-3xl font-extrabold text-white mb-3">
                  {activePillar.title}
                </h3>
                <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
                  {text(`track.${activePillar.id}.description`)}
                </p>
              </div>

              {/* Core Skills Mastered */}
              <div>
                <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-4 font-mono">
                  {text("mastery.skills")}
                </h4>
                <div className="space-y-2.5">
                  {list<string>(`track.${activePillar.id}.skills`).map((skill, i) => (
                    <div key={i} className="flex items-start gap-3 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-xs sm:text-sm text-slate-200">
                      <div className={`w-5 h-5 rounded-full ${activePillar.accentColor} bg-slate-900 flex items-center justify-center shrink-0 mt-0.5 font-bold`}>
                        ✓
                      </div>
                      <span>{skill}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Architectural Step-by-Step Pipeline */}
              <div>
                <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-4 font-mono">
                  {text("mastery.pipeline")}
                </h4>
                <div className="grid sm:grid-cols-2 gap-3">
                  {list<FlowStep>(`track.${activePillar.id}.flow`).map((flow, i) => (
                    <div key={flow.title} className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                      <div className="flex items-center gap-2 text-xs font-mono font-bold text-orange-400 mb-1">
                        <span>{text("mastery.step", { step: activePillar.architectureFlow[i]?.step ?? "" })}</span>
                      </div>
                      <div className="text-xs font-bold text-white mb-1">{flow.title}</div>
                      <div className="text-[11px] text-slate-400 leading-snug">{flow.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Capstone Project & Code Snippet Box */}
            <div className="lg:col-span-5 space-y-6">
              
              {/* Capstone Project Showcase Box */}
              <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950/50 p-6 rounded-2xl border border-indigo-500/30 shadow-xl">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-400 font-mono mb-2">
                  <BookOpen className="w-4 h-4 text-indigo-400" />
                  {text("mastery.capstone")}
                </div>
                <h4 className="text-base sm:text-lg font-bold text-white mb-2">
                  {text(`track.${activePillar.id}.capstoneTitle`)}
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed mb-4">
                  {text(`track.${activePillar.id}.capstoneDescription`)}
                </p>
                <div className="border-t border-slate-800/80 pt-3">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 font-mono">
                    {text("mastery.deliverables")}
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300 font-mono">
                    {list<string>(`track.${activePillar.id}.deliverables`).map((d) => (
                      <li key={d} className="flex items-center gap-2">
                        <span className="text-emerald-400">⚡</span>
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Stack Badges */}
              <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800">
                <div className="text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-3 font-mono">
                  {text("mastery.tools")}
                </div>
                <div className="flex flex-wrap gap-2">
                  {activePillar.techStack.map((tech, i) => (
                    <span
                      key={i}
                      className="bg-slate-900 border border-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-mono font-medium flex items-center gap-1.5"
                    >
                      <span>{tech.logo}</span>
                      <span>{tech.name}</span>
                    </span>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="pt-2 flex flex-col gap-2.5">
                <Link
                  href="/"
                  data-testid="welcome-cta-start"
                  aria-label={text("startDiagnosis")}
                  className="w-full py-3.5 bg-gradient-to-r from-orange-500 to-indigo-600 rounded-xl text-white font-extrabold text-xs uppercase tracking-wider shadow-lg hover:shadow-orange-500/30 transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  <span>{text("startHere")}</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>

            </div>

          </div>

        </div>

      </div>
    </section>
  );
};
