"use client";

import { useState } from "react";
import Link from "next/link";
import { Calculator, TrendingUp, ArrowRight } from 'lucide-react';

const MONTHLY_SUBSCRIPTION_USD = 15;

export function RoiCalculator() {
  const [currentRole, setCurrentRole] = useState<'junior' | 'mid' | 'senior' | 'staff' | 'data'>('senior');
  const [region, setRegion] = useState<'us-hub' | 'us-remote' | 'eu' | 'apac'>('us-hub');
  const [yoe, setYoe] = useState(5);

  const BASE_SALARIES = {
    junior: { 'us-hub': 120000, 'us-remote': 105000, 'eu': 75000, 'apac': 50000 },
    mid: { 'us-hub': 155000, 'us-remote': 135000, 'eu': 95000, 'apac': 65000 },
    senior: { 'us-hub': 195000, 'us-remote': 170000, 'eu': 120000, 'apac': 85000 },
    staff: { 'us-hub': 250000, 'us-remote': 220000, 'eu': 160000, 'apac': 115000 },
    data: { 'us-hub': 165000, 'us-remote': 145000, 'eu': 100000, 'apac': 70000 }
  };

  const BOOST_MULTIPLIER = {
    junior: 1.45,
    mid: 1.42,
    senior: 1.40,
    staff: 1.35,
    data: 1.44
  };

  const currentSalary = Math.round(BASE_SALARIES[currentRole][region] * (1 + (yoe * 0.02)));
  const projectedSalary = Math.round(currentSalary * BOOST_MULTIPLIER[currentRole]);
  const salaryIncrease = projectedSalary - currentSalary;
  
  // Payback in days: $15/mo subscription / daily salary lift (toy math, not placement data)
  const dailyIncrease = salaryIncrease / 365;
  const rawPaybackDays = MONTHLY_SUBSCRIPTION_USD / dailyIncrease;
  const paybackLabel =
    rawPaybackDays < 1 ? "< 1 day of work" : `${Math.round(rawPaybackDays)} days of work`;

  return (
    <section id="calculator" className="py-24 bg-slate-950 border-t border-slate-900 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-bold uppercase tracking-wider mb-4 font-mono">
            <Calculator className="w-3.5 h-3.5" />
            INTERACTIVE SALARY & ROI CALCULATOR
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
            Calculate Your AI Engineering <span className="gradient-text-purple">Compensation Lift</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg">
            Toy payback math against a <strong className="text-slate-200">$15/mo</strong> monthly
            subscription (top of the Labs band). Invented salary lift — not Career Forge placement data.
          </p>
        </div>

        {/* Calculator Interface Box */}
        <div className="glass-panel rounded-3xl p-6 sm:p-10 border border-slate-800 bg-slate-900/90 max-w-5xl mx-auto shadow-2xl">
          <div className="grid lg:grid-cols-12 gap-8 items-center">
            
            {/* Left Controls */}
            <div className="lg:col-span-7 space-y-6">
              
              {/* Current Role Select */}
              <div>
                <label className="block text-xs font-mono font-bold text-slate-300 mb-2 uppercase tracking-wider">
                  CURRENT ROLE / SPECIALIZATION:
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {[
                    { id: 'mid', label: 'Mid SWE' },
                    { id: 'senior', label: 'Senior SWE' },
                    { id: 'staff', label: 'Staff / Tech Lead' },
                    { id: 'data', label: 'Data / ML Eng' },
                    { id: 'junior', label: 'Junior / Associate' }
                  ].map((role) => (
                    <button
                      key={role.id}
                      onClick={() => setCurrentRole(role.id as any)}
                      className={`p-3 rounded-xl text-xs font-semibold transition-all cursor-pointer border ${
                        currentRole === role.id
                          ? 'bg-purple-600 text-white border-purple-400 font-bold shadow'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                      }`}
                    >
                      {role.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Location Select */}
              <div>
                <label className="block text-xs font-mono font-bold text-slate-300 mb-2 uppercase tracking-wider">
                  REGION / COMPENSATION TIER:
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {[
                    { id: 'us-hub', label: 'US Tech Hub (SF/NY)' },
                    { id: 'us-remote', label: 'US Remote' },
                    { id: 'eu', label: 'Europe / UK' },
                    { id: 'apac', label: 'APAC / LATAM' }
                  ].map((loc) => (
                    <button
                      key={loc.id}
                      onClick={() => setRegion(loc.id as any)}
                      className={`p-2.5 rounded-xl text-xs font-medium transition-all cursor-pointer border ${
                        region === loc.id
                          ? 'bg-purple-600 text-white border-purple-400 font-bold shadow'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                      }`}
                    >
                      {loc.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* YOE Slider */}
              <div>
                <div className="flex justify-between text-xs font-mono font-bold text-slate-300 mb-2">
                  <span>YEARS OF SOFTWARE EXPERIENCE:</span>
                  <span className="text-purple-400 font-extrabold text-sm">{yoe} Years</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="15"
                  value={yoe}
                  onChange={(e) => setYoe(Number(e.target.value))}
                  className="w-full accent-purple-500 cursor-pointer"
                />
              </div>

            </div>

            {/* Right Output Box */}
            <div className="lg:col-span-5 bg-gradient-to-br from-slate-950 via-purple-950/40 to-slate-950 p-6 sm:p-8 rounded-2xl border border-purple-500/40 text-center shadow-2xl relative overflow-hidden">
              
              <div className="text-xs font-mono font-extrabold text-purple-400 uppercase tracking-wider mb-2">
                PROJECTED ANNUAL COMPENSATION
              </div>

              <div className="text-4xl sm:text-5xl font-extrabold font-mono text-white mb-2">
                ${projectedSalary.toLocaleString()}
              </div>

              <div className="inline-flex items-center gap-1.5 bg-emerald-500/20 text-emerald-400 font-mono font-extrabold text-sm px-3 py-1 rounded-full border border-emerald-500/30 mb-6">
                <TrendingUp className="w-4 h-4" />
                +${salaryIncrease.toLocaleString()} / year (+{Math.round((BOOST_MULTIPLIER[currentRole] - 1) * 100)}%)
              </div>

              <div className="space-y-3 text-xs font-mono text-left border-t border-slate-800/80 pt-4 mb-6">
                <div className="flex justify-between text-slate-300">
                  <span className="text-slate-400">Current Market Estimate:</span>
                  <span className="font-bold text-slate-200">${currentSalary.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span className="text-slate-400">$15/mo subscription payback:</span>
                  <span className="font-bold text-emerald-400">{paybackLabel}</span>
                </div>
              </div>

              <Link
                href="/"
                data-testid="welcome-cta-start"
                className="w-full py-4 bg-gradient-to-r from-purple-600 via-indigo-600 to-orange-500 rounded-xl text-white font-extrabold text-xs uppercase tracking-wider shadow-lg hover:shadow-purple-500/30 transition-all cursor-pointer flex items-center justify-center gap-2"
              >
                <span>Start diagnosis</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

            </div>

          </div>
        </div>

      </div>
    </section>
  );
};
