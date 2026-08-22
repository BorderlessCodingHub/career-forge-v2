"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { X, Flame, CheckCircle, ArrowRight, Sparkles } from 'lucide-react';
import confetti from 'canvas-confetti';

interface ApplicationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ApplicationModal({ isOpen, onClose }: ApplicationModalProps) {
  const [step, setStep] = useState<number>(1);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    role: 'Senior Software Engineer',
    experienceYears: '3-5 years',
    primaryGoal: 'Become proficient in RAG engineer, Fine-tuner, LLM Evals, OpsLLM',
    preferredTrack: 'Live Cohort Accelerator ($500 Off)',
    linkedinUrl: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  if (!isOpen) return null;

  const handleNext = (e: FormEvent) => {
    e.preventDefault();
    if (step === 1) {
      setStep(2);
    } else {
      setIsSubmitted(true);
      // Trigger confetti!
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 }
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="glass-panel bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 text-slate-400 hover:text-white rounded-full bg-slate-950/80 border border-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {!isSubmitted ? (
          <div>
            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-orange-500/20 border border-orange-500/40 flex items-center justify-center">
                <Flame className="w-5 h-5 text-orange-400 fill-orange-400/20" />
              </div>
              <div>
                <h3 className="text-xl font-extrabold text-white">
                  Apply for Cohort 12
                </h3>
                <p className="text-xs text-orange-400 font-mono">
                  $500 Early Bird Scholarship Applied • 8 Seats Left
                </p>
              </div>
            </div>

            {/* Step Indicators */}
            <div className="flex items-center gap-2 mb-6">
              <div className={`flex-1 h-1.5 rounded-full ${step >= 1 ? 'bg-orange-500' : 'bg-slate-800'}`}></div>
              <div className={`flex-1 h-1.5 rounded-full ${step >= 2 ? 'bg-orange-500' : 'bg-slate-800'}`}></div>
            </div>

            <form onSubmit={handleNext} className="space-y-4">
              {step === 1 ? (
                <>
                  <div>
                    <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                      FULL NAME:
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Sarah Connor"
                      value={formData.fullName}
                      onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                      WORK EMAIL ADDRESS:
                    </label>
                    <input
                      type="email"
                      required
                      placeholder="e.g. sarah@techcorp.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                      CURRENT ROLE / TITLE:
                    </label>
                    <select
                      value={formData.role}
                      onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono"
                    >
                      <option value="Senior Software Engineer">Senior Software Engineer</option>
                      <option value="Backend Developer">Backend / Systems Engineer</option>
                      <option value="Full-Stack Developer">Full-Stack Engineer</option>
                      <option value="Data / ML Engineer">Data / Machine Learning Engineer</option>
                      <option value="Engineering Manager / Lead">Tech Lead / Engineering Manager</option>
                    </select>
                  </div>

                  <button
                    type="submit"
                    className="w-full mt-4 py-3.5 bg-gradient-to-r from-orange-500 to-indigo-600 rounded-xl text-white font-extrabold text-xs uppercase tracking-wider shadow-lg hover:shadow-orange-500/20 transition-all cursor-pointer flex items-center justify-center gap-2"
                  >
                    <span>Next: Select Goal & Track</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                      PRIMARY CAREER GOAL:
                    </label>
                    <input
                      type="text"
                      readOnly
                      value={formData.primaryGoal}
                      className="w-full bg-slate-950/80 border border-orange-500/40 rounded-xl px-4 py-2.5 text-xs text-orange-300 font-mono font-semibold"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                      PREFERRED ENROLLMENT TRACK:
                    </label>
                    <select
                      value={formData.preferredTrack}
                      onChange={(e) => setFormData({ ...formData, preferredTrack: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono"
                    >
                      <option value="Live Cohort Accelerator ($500 Off)">Live Cohort Accelerator ($2,999 - $500 Off)</option>
                      <option value="Self-Paced Engineering Track">Self-Paced Track ($1,499)</option>
                      <option value="Enterprise / Team Training">Enterprise Team Training</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                      LINKEDIN / GITHUB LINK (OPTIONAL):
                    </label>
                    <input
                      type="url"
                      placeholder="https://linkedin.com/in/username"
                      value={formData.linkedinUrl}
                      onChange={(e) => setFormData({ ...formData, linkedinUrl: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono"
                    />
                  </div>

                  <div className="flex gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="w-1/3 py-3 bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold cursor-pointer"
                    >
                      Back
                    </button>
                    <button
                      type="submit"
                      className="w-2/3 py-3 bg-gradient-to-r from-orange-500 via-amber-500 to-indigo-600 text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-lg hover:shadow-orange-500/30 transition-all cursor-pointer flex items-center justify-center gap-1.5"
                    >
                      <span>Submit Application</span>
                      <Sparkles className="w-4 h-4" />
                    </button>
                  </div>
                </>
              )}
            </form>
          </div>
        ) : (
          <div className="text-center py-8 space-y-4 animate-in zoom-in-95 duration-300">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mx-auto mb-2">
              <CheckCircle className="w-10 h-10" />
            </div>

            <h3 className="text-2xl font-extrabold text-white">
              Application Submitted Successfully!
            </h3>

            <p className="text-xs text-slate-300 max-w-md mx-auto leading-relaxed">
              Congratulations <strong className="text-white">{formData.fullName}</strong>! Your application for <strong>Cohort 12</strong> has been prioritized with the <strong>$500 Early Bird Scholarship</strong>.
            </p>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 max-w-md mx-auto text-xs font-mono text-slate-400 space-y-1 text-left">
              <div>• Instant eligibility status: <span className="text-emerald-400 font-bold">APPROVED</span></div>
              <div>• Confirmation sent to: <span className="text-white">{formData.email}</span></div>
              <div>• An admissions lead will contact you within 4 hours.</div>
            </div>

            <button
              onClick={onClose}
              className="mt-4 px-8 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl font-mono font-bold text-xs cursor-pointer"
            >
              Return to Website
            </button>
          </div>
        )}

      </div>
    </div>
  );
};
