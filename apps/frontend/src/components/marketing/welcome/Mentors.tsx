"use client";

import { MENTORS } from "./data/curriculumData";
import { Award } from "lucide-react";
import { welcomeAssetPath } from "@/lib/welcome-assets";

export function Mentors() {
  return (
    <section className="py-24 bg-slate-950 border-t border-slate-900 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-4 font-mono">
            <Award className="w-3.5 h-3.5" />
            BORDERLESS TEAM
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            The ecosystem team behind <span className="gradient-text-cyan">Career Forge</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Built so you can see your starting point, watch a live roadmap take shape, and prove
            what you can do.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
          {MENTORS.map((mentor) => (
            <div
              key={mentor.name}
              className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 bg-slate-900/80 hover:border-slate-700 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="relative mb-6">
                  {/* eslint-disable-next-line @next/next/no-img-element -- local Welcome mentor photos */}
                  <img
                    src={welcomeAssetPath("mentors", mentor.avatar)}
                    alt={mentor.name}
                    className="w-20 h-20 rounded-2xl object-cover border-2 border-slate-700 group-hover:border-indigo-500 transition-colors shadow-lg"
                  />
                </div>

                <h3 className="text-xl font-bold text-white mb-1">{mentor.name}</h3>
                <p className="text-xs font-mono font-semibold text-indigo-400 mb-4">{mentor.role}</p>

                <p className="text-xs text-slate-300 leading-relaxed mb-6">{mentor.bio}</p>
              </div>

              <div className="pt-4 border-t border-slate-800">
                <span className="text-[11px] font-mono font-bold text-slate-400 bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                  {mentor.specialty}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
