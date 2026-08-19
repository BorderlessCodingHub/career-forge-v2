import React, { useState } from 'react';
import { X, Calendar, Clock, CheckCircle, ArrowRight } from 'lucide-react';

interface StrategyCallModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const StrategyCallModal: React.FC<StrategyCallModalProps> = ({ isOpen, onClose }) => {
  const [selectedSlot, setSelectedSlot] = useState('Tomorrow @ 2:00 PM EST');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [booked, setBooked] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setBooked(true);
  };

  const slots = [
    'Tomorrow @ 11:00 AM EST',
    'Tomorrow @ 2:00 PM EST',
    'Tomorrow @ 4:30 PM EST',
    'Thursday @ 1:00 PM EST',
    'Friday @ 3:00 PM EST'
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="glass-panel bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl relative">
        
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 text-slate-400 hover:text-white rounded-full bg-slate-950/80 border border-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {!booked ? (
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-orange-500/20 border border-orange-500/40 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-orange-400" />
              </div>
              <div>
                <h3 className="text-xl font-extrabold text-white">
                  Book 1-on-1 Strategy Call
                </h3>
                <p className="text-xs text-orange-400 font-mono">
                  15-Min System Design & Career Evaluation
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed mb-6">
              Discuss your background, inspect syllabus details, and determine eligibility for Cohort 12 with a lead AI instructor.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                  FULL NAME:
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Alex Rivera"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
                  EMAIL ADDRESS:
                </label>
                <input
                  type="email"
                  required
                  placeholder="e.g. alex@developer.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-orange-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-mono font-bold text-slate-300 mb-2">
                  SELECT AVAILABLE TIME SLOT:
                </label>
                <div className="space-y-2">
                  {slots.map((s, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => setSelectedSlot(s)}
                      className={`w-full p-2.5 rounded-xl text-xs font-mono font-bold text-left transition-all cursor-pointer border flex items-center justify-between ${
                        selectedSlot === s
                          ? 'bg-orange-500 text-slate-950 border-orange-400 shadow'
                          : 'bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <span>{s}</span>
                      <Clock className="w-3.5 h-3.5 opacity-80" />
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3.5 bg-gradient-to-r from-orange-500 via-amber-500 to-indigo-600 rounded-xl text-white font-extrabold text-xs uppercase tracking-wider shadow-lg hover:shadow-orange-500/25 transition-all cursor-pointer flex items-center justify-center gap-2"
              >
                <span>Confirm Strategy Call</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          </div>
        ) : (
          <div className="text-center py-6 space-y-4">
            <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center mx-auto">
              <CheckCircle className="w-8 h-8" />
            </div>

            <h3 className="text-xl font-bold text-white">
              Call Confirmed!
            </h3>

            <p className="text-xs text-slate-300">
              A calendar invite and Google Meet link have been sent to <strong className="text-white">{email}</strong> for <strong>{selectedSlot}</strong>.
            </p>

            <button
              onClick={onClose}
              className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono rounded-xl cursor-pointer"
            >
              Done
            </button>
          </div>
        )}

      </div>
    </div>
  );
};
