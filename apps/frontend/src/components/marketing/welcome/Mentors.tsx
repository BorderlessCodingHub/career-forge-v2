"use client";

import { MENTORS } from './data/curriculumData';
import { Award } from 'lucide-react';

export function Mentors() {
  return (
    <section className="py-24 bg-slate-950 border-t border-slate-900 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-4 font-mono">
            <Award className="w-3.5 h-3.5" />
            WORLD-CLASS AI INSTRUCTORS
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            Learn Directly From Practitioners Who <span className="gradient-text-cyan">Built Production AI</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            No academic theorists. Every mentor active on the frontlines of AI infrastructure, vector engines, and model alignment.
          </p>
        </div>

        {/* Mentor Cards Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {MENTORS.map((mentor, index) => (
            <div
              key={index}
              className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 bg-slate-900/80 hover:border-slate-700 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="relative mb-6">
                  <img
                    src={mentor.avatar}
                    alt={mentor.name}
                    className="w-20 h-20 rounded-2xl object-cover border-2 border-slate-700 group-hover:border-indigo-500 transition-colors shadow-lg"
                  />
                  <div className="absolute -bottom-2 left-14 bg-slate-950 px-2 py-0.5 rounded border border-slate-800 text-[10px] font-mono text-orange-400 font-bold">
                    EX-TOP LABS
                  </div>
                </div>

                <h3 className="text-xl font-bold text-white mb-1">
                  {mentor.name}
                </h3>
                <p className="text-xs font-mono font-semibold text-indigo-400 mb-4">
                  {mentor.role}
                </p>

                <p className="text-xs text-slate-300 leading-relaxed mb-6">
                  {mentor.bio}
                </p>
              </div>

              <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
                <span className="text-[11px] font-mono font-bold text-slate-400 bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                  {mentor.specialty}
                </span>

                <div className="flex items-center gap-2">
                  <a
                    href={mentor.github}
                    target="_blank"
                    rel="noreferrer"
                    className="px-2.5 py-1 rounded-lg bg-slate-950 text-slate-300 hover:text-white border border-slate-800 text-xs font-mono font-bold transition-colors"
                  >
                    GitHub Profile
                  </a>
                  <a
                    href={mentor.linkedin}
                    target="_blank"
                    rel="noreferrer"
                    className="px-2.5 py-1 rounded-lg bg-slate-950 text-indigo-400 hover:text-indigo-300 border border-slate-800 text-xs font-mono font-bold transition-colors"
                  >
                    LinkedIn
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
};
