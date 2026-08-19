import React, { useState } from 'react';
import { X, Download, FileText, CheckCircle } from 'lucide-react';

interface SyllabusModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SyllabusModal: React.FC<SyllabusModalProps> = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState('');
  const [downloaded, setDownloaded] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setDownloaded(true);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="glass-panel bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl relative">
        
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 text-slate-400 hover:text-white rounded-full bg-slate-950/80 border border-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {!downloaded ? (
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center">
                <FileText className="w-5 h-5 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-xl font-extrabold text-white">
                  Download 2026 AI Curriculum
                </h3>
                <p className="text-xs text-indigo-400 font-mono">
                  Full 12-Week Syllabus & Project Repositories
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed mb-6">
              Get instant PDF access to complete week-by-week lab breakdowns, Unsloth QLoRA fine-tuning configs, DeepEval assertion benchmarks, and vLLM architecture blueprints.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                  ENTER YOUR WORK EMAIL:
                </label>
                <input
                  type="email"
                  required
                  placeholder="e.g. dev@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3.5 bg-gradient-to-r from-indigo-600 via-purple-600 to-orange-500 rounded-xl text-white font-extrabold text-xs uppercase tracking-wider shadow-lg hover:shadow-indigo-500/30 transition-all cursor-pointer flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                <span>Instant Download Syllabus PDF</span>
              </button>
            </form>
          </div>
        ) : (
          <div className="text-center py-6 space-y-4">
            <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center mx-auto">
              <CheckCircle className="w-8 h-8" />
            </div>

            <h3 className="text-xl font-bold text-white">
              Syllabus Downloading!
            </h3>

            <p className="text-xs text-slate-300">
              We've sent a copy to <strong className="text-white">{email}</strong>.
            </p>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-left text-xs font-mono text-slate-300 space-y-1.5">
              <div className="text-emerald-400 font-bold">📄 PDF Highlights:</div>
              <div>• 4 Core Capstone Repository Schemas</div>
              <div>• $500 Nvidia Cloud GPU Redemption Key Info</div>
              <div>• Weekly Live Workshop Calendar & Mentors</div>
            </div>

            <button
              onClick={onClose}
              className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono rounded-xl cursor-pointer"
            >
              Close Window
            </button>
          </div>
        )}

      </div>
    </div>
  );
};
