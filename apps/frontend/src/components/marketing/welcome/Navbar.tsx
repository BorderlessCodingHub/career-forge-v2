"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Flame, Sparkles, Menu, X, ArrowRight, ChevronRight, Clock } from "lucide-react";

interface NavbarProps {
  onOpenApplyModal: () => void;
  onOpenSyllabusModal: () => void;
  onOpenStrategyModal: () => void;
}

export function Navbar({
  onOpenApplyModal,
  onOpenSyllabusModal,
  onOpenStrategyModal
}: NavbarProps) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [timeLeft, setTimeLeft] = useState({ days: 4, hours: 14, mins: 32, secs: 45 });

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);

    // Countdown timer interval
    const interval = setInterval(() => {
      setTimeLeft(prev => {
        if (prev.secs > 0) return { ...prev, secs: prev.secs - 1 };
        if (prev.mins > 0) return { ...prev, mins: 59, secs: 59 };
        if (prev.hours > 0) return { ...prev, hours: prev.hours - 1, mins: 59, secs: 59 };
        if (prev.days > 0) return { ...prev, days: prev.days - 1, hours: 23, mins: 59, secs: 59 };
        return prev;
      });
    }, 1000);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      clearInterval(interval);
    };
  }, []);

  const scrollToSection = (id: string) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      {/* Top Countdown & Announcement Bar */}
      <div className="bg-gradient-to-r from-orange-900/90 via-indigo-950 to-slate-900 border-b border-orange-500/20 text-xs font-medium py-2 px-4 text-center text-slate-200 flex flex-wrap items-center justify-center gap-2 sm:gap-4 relative z-50">
        <span className="inline-flex items-center gap-1.5 bg-orange-500/20 text-orange-400 font-semibold px-2 py-0.5 rounded-full border border-orange-500/30">
          <span className="w-2 h-2 rounded-full bg-orange-400 animate-pulse"></span>
          COHORT 12 APPLICATIONS OPEN
        </span>
        <span className="hidden sm:inline text-slate-400">•</span>
        <span className="text-slate-300">
          Early Bird $500 Scholarship Ends In:
        </span>
        <div className="inline-flex items-center gap-1 font-mono text-orange-300 font-bold bg-slate-900/70 px-2 py-0.5 rounded border border-slate-700">
          <Clock className="w-3 h-3 text-orange-400" />
          <span>{timeLeft.days}d</span>:<span>{String(timeLeft.hours).padStart(2, '0')}h</span>:
          <span>{String(timeLeft.mins).padStart(2, '0')}m</span>:<span>{String(timeLeft.secs).padStart(2, '0')}s</span>
        </div>
        <button
          onClick={onOpenApplyModal}
          className="underline hover:text-white font-semibold text-orange-300 ml-1 transition-colors flex items-center gap-0.5 cursor-pointer"
        >
          Claim Scholarship <ChevronRight className="w-3 h-3 inline" />
        </button>
      </div>

      {/* Main Sticky Glass Header */}
      <header
        className={`sticky top-0 z-40 transition-all duration-300 ${
          isScrolled
            ? 'glass-panel bg-slate-950/85 backdrop-blur-md shadow-2xl py-3 border-b border-slate-800/80'
            : 'bg-transparent py-4 border-b border-slate-800/40'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          {/* Brand Logo */}
          <div
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-500 via-amber-500 to-indigo-600 p-0.5 shadow-lg shadow-orange-500/20 group-hover:shadow-orange-500/40 transition-all duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Flame className="w-5 h-5 text-orange-400 group-hover:scale-110 transition-transform duration-300 fill-orange-400/20" />
              </div>
            </div>
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

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-7 text-sm font-medium text-slate-300">
            <button
              onClick={() => scrollToSection('pillars')}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              4 Core Pillars
            </button>
            <button
              onClick={() => scrollToSection('sandbox')}
              className="hover:text-cyan-400 transition-colors flex items-center gap-1 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              Live AI Sandbox
            </button>
            <button
              onClick={() => scrollToSection('curriculum')}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              12-Week Syllabus
            </button>
            <button
              onClick={() => scrollToSection('calculator')}
              className="hover:text-purple-400 transition-colors cursor-pointer"
            >
              ROI Calculator
            </button>
            <button
              onClick={() => scrollToSection('testimonials')}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              Alumni Success
            </button>
            <button
              onClick={() => scrollToSection('pricing')}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              Tuition & Plans
            </button>
            <button
              onClick={() => scrollToSection('faq')}
              className="hover:text-orange-400 transition-colors cursor-pointer"
            >
              FAQ
            </button>
          </nav>

          {/* Action CTAs */}
          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={onOpenSyllabusModal}
              className="text-xs font-semibold px-3.5 py-2 text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 rounded-lg transition-all cursor-pointer"
            >
              Download Syllabus
            </button>

            <Link
              href="/"
              data-testid="welcome-cta-start"
              className="relative group text-xs font-bold px-4 py-2.5 rounded-lg text-white shimmer-button shadow-lg shadow-indigo-500/20 hover:shadow-orange-500/30 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span>Start diagnosis</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>

          {/* Mobile Menu Button */}
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

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden glass-panel bg-slate-950/95 border-b border-slate-800 px-4 pt-3 pb-6 mt-2 space-y-3 shadow-2xl animate-in slide-in-from-top duration-200">
            <button
              onClick={() => scrollToSection('pillars')}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              4 Core Pillars
            </button>
            <button
              onClick={() => scrollToSection('sandbox')}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-cyan-400 font-medium flex items-center gap-1.5"
            >
              <Sparkles className="w-4 h-4 text-cyan-400" />
              Live AI Sandbox Demo
            </button>
            <button
              onClick={() => scrollToSection('curriculum')}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              12-Week Syllabus
            </button>
            <button
              onClick={() => scrollToSection('calculator')}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-purple-400 font-medium"
            >
              Salary & ROI Calculator
            </button>
            <button
              onClick={() => scrollToSection('testimonials')}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              Alumni Reviews
            </button>
            <button
              onClick={() => scrollToSection('pricing')}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              Tuition & Pricing
            </button>
            <button
              onClick={() => scrollToSection('faq')}
              className="block w-full text-left py-2 text-sm text-slate-200 hover:text-orange-400 font-medium"
            >
              FAQ
            </button>

            <div className="pt-3 border-t border-slate-800 flex flex-col gap-2">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  onOpenSyllabusModal();
                }}
                className="w-full text-center py-2.5 text-xs font-semibold text-slate-200 bg-slate-800 rounded-lg"
              >
                Download Syllabus PDF
              </button>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  onOpenStrategyModal();
                }}
                className="w-full text-center py-2.5 text-xs font-semibold text-slate-300 bg-slate-900 border border-slate-700 rounded-lg"
              >
                Book 1-on-1 Strategy Call
              </button>
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
};
