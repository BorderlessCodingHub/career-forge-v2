"use client";

import { useState } from "react";
import Link from "next/link";
import { ROADMAP_WEEKS } from './data/curriculumData';
import { Calendar, CheckCircle2, ChevronDown, ChevronUp, Terminal, GitPullRequest, ArrowRight } from 'lucide-react';

export function CurriculumRoadmap() {
  const [expandedIndex, setExpandedIndex] = useState<number>(0);

  return (
    <section id="curriculum" className="py-24 bg-slate-950 border-t border-slate-900 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-bold uppercase tracking-wider mb-4 font-mono">
            <Calendar className="w-3.5 h-3.5" />
            12-WEEK IMMERSIVE ROADMAP
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            Structured for Production Mastery, <span className="gradient-text-orange">Not Toy Demos</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            A 12-week, four-phase map of production AI work — RAG, Fine-Tuning, Evals, and OpsLLM.
            Chrome only: not a live cohort calendar.
          </p>
        </div>

        {/* PR Review Feature Highlight */}
        <div className="glass-panel p-5 rounded-2xl border border-indigo-500/30 bg-slate-900/80 mb-12 max-w-4xl mx-auto flex flex-wrap items-center justify-between gap-4 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0">
              <GitPullRequest className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2">
                Four phases of production AI work
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                RAG, fine-tuning, evals, and OpsLLM — a 12-week map, not a live enrollment window.
              </p>
            </div>
          </div>
        </div>

        {/* Timeline List Accordion */}
        <div className="max-w-4xl mx-auto space-y-4">
          {ROADMAP_WEEKS.map((item, index) => {
            const isExpanded = expandedIndex === index;
            return (
              <div
                key={index}
                className={`glass-panel rounded-2xl overflow-hidden transition-all border ${
                  isExpanded ? 'border-orange-500/40 bg-slate-900 shadow-2xl' : 'border-slate-800 bg-slate-950/80 hover:border-slate-700'
                }`}
              >
                {/* Accordion Header */}
                <div
                  onClick={() => setExpandedIndex(isExpanded ? -1 : index)}
                  className="p-5 sm:p-6 cursor-pointer flex items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-slate-950 border border-slate-800 flex flex-col items-center justify-center shrink-0 font-mono">
                      <span className="text-[10px] text-slate-500 uppercase">Phase</span>
                      <span className="text-sm font-extrabold text-orange-400">0{index + 1}</span>
                    </div>

                    <div>
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span className="text-xs font-mono font-bold text-orange-400 bg-orange-950/60 px-2 py-0.5 rounded border border-orange-500/30">
                          {item.week}
                        </span>
                        <span className="text-xs text-slate-400 font-mono hidden sm:inline">
                          {item.phase}
                        </span>
                      </div>
                      <h3 className="text-base sm:text-xl font-bold text-white">
                        {item.title}
                      </h3>
                    </div>
                  </div>

                  <div className="p-2 rounded-lg bg-slate-800 text-slate-400">
                    {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-5 pb-6 sm:px-6 sm:pb-6 border-t border-slate-800/80 pt-5 space-y-6">
                    <div>
                      <h4 className="text-xs font-mono font-extrabold text-slate-400 uppercase tracking-wider mb-3">
                        WEEKLY TOPICS COVERED:
                      </h4>
                      <div className="grid sm:grid-cols-2 gap-2">
                        {item.topics.map((t, i) => (
                          <div key={i} className="flex items-center gap-2 text-xs text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                            <CheckCircle2 className="w-4 h-4 text-orange-400 shrink-0" />
                            <span>{t}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Capstone Project Deliverable */}
                    <div className="bg-slate-950 p-4 rounded-xl border border-indigo-500/20">
                      <div className="text-xs font-mono font-bold text-indigo-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <Terminal className="w-3.5 h-3.5" />
                        PHASE CAPSTONE DELIVERABLE:
                      </div>
                      <p className="text-xs text-slate-200 font-semibold">
                        {item.project}
                      </p>
                    </div>

                    {/* Tech Badges */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800/60">
                      <div className="flex flex-wrap gap-1.5">
                        {item.tech.map((t, idx) => (
                          <span key={idx} className="bg-slate-800 text-slate-300 px-2.5 py-1 rounded text-[11px] font-mono border border-slate-700">
                            {t}
                          </span>
                        ))}
                      </div>
                      <Link
                        href="/"
                        className="text-xs font-mono font-bold text-orange-400 hover:text-orange-300 flex items-center gap-1 cursor-pointer"
                      >
                        <span>Start diagnosis</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-12">
          <Link
            href="/"
            data-testid="welcome-cta-start"
            className="px-8 py-4 bg-gradient-to-r from-orange-500 via-amber-500 to-indigo-600 rounded-xl text-white font-extrabold text-sm shadow-xl hover:shadow-orange-500/25 transition-all cursor-pointer inline-flex items-center gap-2"
          >
            <span>Start diagnosis</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

      </div>
    </section>
  );
};
