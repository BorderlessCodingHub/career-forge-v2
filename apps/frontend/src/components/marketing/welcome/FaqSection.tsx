"use client";

import { useState } from "react";
import Link from "next/link";
import { FAQS } from "./data/curriculumData";
import { HelpCircle, ChevronDown, ChevronUp, Search, MessageSquare } from "lucide-react";

export function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredFaqs = FAQS.filter(
    (faq) =>
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <section id="faq" className="py-24 bg-slate-950 border-t border-slate-900 relative">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-4 font-mono">
            <HelpCircle className="w-3.5 h-3.5" />
            FREQUENTLY ASKED QUESTIONS
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            Everything You Need To Know
          </h2>
          <p className="text-slate-400 text-base">
            Membership, how to start, and what the product actually does — no cohort schedules or
            career guarantees.
          </p>
        </div>

        <div className="relative mb-8">
          <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search FAQ (e.g. membership, diagnosis, laptop)..."
            className="w-full bg-slate-900 border border-slate-800 rounded-2xl pl-11 pr-4 py-3.5 text-xs sm:text-sm text-slate-200 placeholder-slate-500 font-mono focus:outline-none focus:border-cyan-500 shadow-inner"
          />
        </div>

        <div className="space-y-4">
          {filteredFaqs.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div
                key={faq.question}
                className={`glass-panel rounded-2xl overflow-hidden transition-all border ${
                  isOpen
                    ? "border-indigo-500/40 bg-slate-900 shadow-xl"
                    : "border-slate-800 bg-slate-950/80 hover:border-slate-700"
                }`}
              >
                <button
                  onClick={() => setOpenIndex(isOpen ? -1 : index)}
                  className="w-full p-5 sm:p-6 text-left flex items-center justify-between gap-4 cursor-pointer"
                >
                  <span className="text-base sm:text-lg font-bold text-white pr-2">{faq.question}</span>
                  <div className="p-2 rounded-lg bg-slate-800 text-slate-400 shrink-0">
                    {isOpen ? (
                      <ChevronUp className="w-5 h-5 text-indigo-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5" />
                    )}
                  </div>
                </button>

                {isOpen && (
                  <div className="px-5 pb-6 sm:px-6 sm:pb-6 border-t border-slate-800/80 pt-4 text-sm text-slate-300 leading-relaxed font-normal">
                    {faq.answer}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="mt-12 text-center bg-slate-900/60 p-6 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-left">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0">
              <MessageSquare className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">Ready to see where you stand?</div>
              <p className="text-xs text-slate-400">
                Start diagnosis — Email identity happens in the product, not here.
              </p>
            </div>
          </div>
          <Link
            href="/"
            data-testid="welcome-cta-start"
            aria-label="Start diagnosis"
            className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono font-bold text-xs rounded-xl border border-slate-700 transition-colors cursor-pointer"
          >
            Start here
          </Link>
        </div>
      </div>
    </section>
  );
}
