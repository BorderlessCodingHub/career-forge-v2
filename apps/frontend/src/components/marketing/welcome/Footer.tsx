"use client";

import Link from "next/link";

import { BrandMark } from "@/components/ui/BrandMark";
import { useWelcomeText } from "./useWelcomeText";

export function Footer() {
  const { text } = useWelcomeText();
  return (
    <footer className="bg-slate-950 border-t border-slate-900 pt-16 pb-12 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 pb-12 border-b border-slate-900">
          <div className="col-span-2">
            <div className="flex items-center gap-2.5 mb-4">
              <BrandMark size={32} />
              <span className="font-extrabold text-lg text-white font-mono">
                CAREER<span className="text-orange-400">FORGE</span>
              </span>
            </div>

            <p className="text-slate-400 text-xs leading-relaxed max-w-sm mb-4">
              {text("footer.blurb")}
            </p>

            <div className="inline-flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-[11px] font-mono text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>{text("footer.chip")}</span>
            </div>
          </div>

          <div>
            <h4 className="font-mono text-xs font-bold text-white uppercase tracking-wider mb-4">
              {text("footer.pillars")}
            </h4>
            <ul className="space-y-2.5 text-slate-400">
              <li>
                <a href="#pillars" className="hover:text-orange-400 transition-colors">
                  {text("footer.pillarRag")}
                </a>
              </li>
              <li>
                <a href="#pillars" className="hover:text-purple-400 transition-colors">
                  {text("footer.pillarTune")}
                </a>
              </li>
              <li>
                <a href="#pillars" className="hover:text-cyan-400 transition-colors">
                  {text("footer.pillarEvals")}
                </a>
              </li>
              <li>
                <a href="#pillars" className="hover:text-emerald-400 transition-colors">
                  {text("footer.pillarOps")}
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-mono text-xs font-bold text-white uppercase tracking-wider mb-4">
              {text("footer.resources")}
            </h4>
            <ul className="space-y-2.5 text-slate-400">
              <li>
                <a href="#sandbox" className="hover:text-white transition-colors">
                  {text("footer.sandbox")}
                </a>
              </li>
              <li>
                <a href="#calculator" className="hover:text-white transition-colors">
                  {text("footer.calculator")}
                </a>
              </li>
              <li>
                <a href="#testimonials" className="hover:text-white transition-colors">
                  {text("stories")}
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-mono text-xs font-bold text-white uppercase tracking-wider mb-4">
              {text("footer.getStarted")}
            </h4>
            <ul className="space-y-2.5 text-slate-400">
              <li>
                <Link
                  href="/"
                  aria-label={text("startDiagnosis")}
                  className="hover:text-orange-400 font-bold transition-colors cursor-pointer text-left"
                >
                  {text("startHere")}
                </Link>
              </li>
              <li>
                <a href="#pricing" className="hover:text-white transition-colors">
                  {text("access")}
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-white transition-colors">
                  {text("footer.admissions")}
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500 font-mono">
          <div>
            {text("footer.legal")}
          </div>

          <div className="flex items-center gap-4">
            <a href="#" className="hover:text-slate-300 transition-colors">
              {text("footer.privacy")}
            </a>
            <span>•</span>
            <a href="#" className="hover:text-slate-300 transition-colors">
              {text("footer.terms")}
            </a>
            <span>•</span>
            <a href="#" className="hover:text-slate-300 transition-colors">
              {text("footer.security")}
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
