"use client";

import { EMPLOYERS } from "./data/curriculumData";
import { welcomeAssetPath } from "@/lib/welcome-assets";

export function SocialProof() {
  return (
    <section className="py-12 bg-slate-950/90 border-y border-slate-800/80 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-slate-400 mb-8">
          Companies where Borderless BASE & PSP talents work
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 items-center justify-center opacity-80 hover:opacity-100 transition-opacity">
          {EMPLOYERS.map((item) => (
            <div
              key={item.name}
              className="glass-panel p-3 rounded-lg border border-slate-800 text-center hover:border-slate-700 hover:bg-slate-900 transition-all group flex items-center justify-center min-h-[72px]"
            >
              {/* eslint-disable-next-line @next/next/no-img-element -- local Welcome proof assets */}
              <img
                src={welcomeAssetPath("employers", item.logo)}
                alt={item.name}
                className="max-h-10 max-w-full object-contain"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
