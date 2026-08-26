"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Sparkles, Menu, X, ArrowRight, ChevronRight } from "lucide-react";

import { BrandMark } from "@/components/ui/BrandMark";

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <>
      <div className="bg-gradient-to-r from-orange-900/90 via-indigo-950 to-slate-900 border-b border-orange-500/20 text-xs font-medium py-2 px-4 text-center text-slate-200 flex flex-wrap items-center justify-center gap-2 sm:gap-4 relative z-50">
        <span className="inline-flex items-center gap-1.5 bg-orange-500/20 text-orange-400 font-semibold px-2 py-0.5 rounded-full border border-orange-500/30">
          <span className="w-2 h-2 rounded-full bg-orange-400 animate-pulse"></span>
          BASE · PSP
        </span>
        <span className="hidden sm:inline text-slate-400">•</span>
        <span className="text-slate-300">
          Members: Career Forge is included. Start diagnosis with your member email.
        </span>
        <Link
          href="/"
          data-testid="welcome-bar-cta"
          className="underline hover:text-white font-semibold text-orange-300 ml-1 transition-colors flex items-center gap-0.5 cursor-pointer"
        >
          Start diagnosis <ChevronRight className="w-3 h-3 inline" />
        </Link>
      </div>

      <header
        className={`sticky top-0 z-40 transition-all duration-300 ${
          isScrolled
            ? "glass-panel bg-slate-950/85 backdrop-blur-md shadow-2xl py-3 border-b border-slate-800/80"
            : "bg-transparent py-4 border-b border-slate-800/40"
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <div
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <BrandMark
              size={40}
              className="group-hover:scale-110 transition-transform duration-300"
            />
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-xl tracking-tight text-white font-mono">
                  CAREER<span className="text-orange-400">FORGE</span>
                </span>
                <span className="bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded">
                  AI Track
                </span>
              </div>
              <p className="text-[10px] text-slate-400 -mt-1 font-mono">
                RAG • Fine-Tuning • Evals • OpsLLM
              </p>
            </div>
          </div>

          <nav className="hidden lg:flex items-center gap-7 text-sm font-medium text-slate-300">
            <button
              onClick={() => scrollToSection("pillars")}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              4 Core Pillars
            </button>
            <button
              onClick={() => scrollToSection("sandbox")}
              className="hover:text-cyan-400 transition-colors flex items-center gap-1 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              Live AI Sandbox
            </button>
            <button
              onClick={() => scrollToSection("curriculum")}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              12-Week Syllabus
            </button>
            <button
              onClick={() => scrollToSection("calculator")}
              className="hover:text-purple-400 transition-colors cursor-pointer"
            >
              ROI Calculator
            </button>
            <button
              onClick={() => scrollToSection("testimonials")}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              Stories
            </button>
            <button
              onClick={() => scrollToSection("pricing")}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              Access
            </button>
            <button
              onClick={() => scrollToSection("faq")}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              FAQ
            </button>
          </nav>

          <div className="hidden md:flex items-center gap-3">
            <a
              href="#curriculum"
              className="text-xs font-semibold px-3.5 py-2 text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 rounded-lg transition-all cursor-pointer"
            >
              Download Syllabus
            </a>

            <Link
              href="/"
              data-testid="welcome-cta-start"
              className="relative group text-xs font-bold px-4 py-2.5 rounded-lg text-white shimmer-button shadow-lg shadow-indigo-500/20 hover:shadow-orange-500/30 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span>Start diagnosis</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>

          <div className="flex lg:hidden items-center gap-2">
            <Link
              href="/"
              data-testid="welcome-cta-start"
              className="text-xs font-bold px-3 py-1.5 bg-gradient-to-r from-orange-500 to-indigo-600 rounded-md text-white cursor-pointer"
            >
              Start diagnosis
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-300 hover:text-white rounded-lg bg-slate-900 border border-slate-800 focus:outline-none cursor-pointer"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="lg:hidden glass-panel bg-slate-950/95 border-b border-slate-800 px-4 pt-3 pb-6 mt-2 space-y-3 shadow-2xl animate-in slide-in-from-top duration-200">
            <button
              onClick={() => scrollToSection("pillars")}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              4 Core Pillars
            </button>
            <button
              onClick={() => scrollToSection("sandbox")}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-cyan-400 font-medium flex items-center gap-1.5"
            >
              <Sparkles className="w-4 h-4 text-cyan-400" />
              Live AI Sandbox Demo
            </button>
            <button
              onClick={() => scrollToSection("curriculum")}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              12-Week Syllabus
            </button>
            <button
              onClick={() => scrollToSection("calculator")}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-purple-400 font-medium"
            >
              Salary & ROI Calculator
            </button>
            <button
              onClick={() => scrollToSection("testimonials")}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              Stories
            </button>
            <button
              onClick={() => scrollToSection("pricing")}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              Access
            </button>
            <button
              onClick={() => scrollToSection("faq")}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              FAQ
            </button>

            <div className="pt-3 border-t border-slate-800 flex flex-col gap-2">
              <a
                href="#curriculum"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 text-xs font-semibold text-slate-200 bg-slate-800 rounded-lg"
              >
                Download Syllabus
              </a>
              <Link
                href="/"
                data-testid="welcome-cta-start"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 text-xs font-bold text-white bg-gradient-to-r from-orange-500 via-amber-500 to-indigo-600 rounded-lg shadow-lg"
              >
                Start diagnosis
              </Link>
            </div>
          </div>
        )}
      </header>
    </>
  );
}
