"use client";

import { CtaSection } from "./CtaSection";
import { FaqSection } from "./FaqSection";
import { Footer } from "./Footer";
import { Hero } from "./Hero";
import { IndustryProblem } from "./IndustryProblem";
import { InteractiveSandbox } from "./InteractiveSandbox";
import { Mentors } from "./Mentors";
import { Navbar } from "./Navbar";
import { PillarsOverview } from "./PillarsOverview";
import { Pricing } from "./Pricing";
import { RoiCalculator } from "./RoiCalculator";
import { SocialProof } from "./SocialProof";
import { Testimonials } from "./Testimonials";

import "./welcome.css";

type WelcomeShellProps = {
  className?: string;
};

export function WelcomeShell({ className }: WelcomeShellProps) {
  return (
    <div
      className={`welcome-premium min-h-screen bg-slate-950 text-slate-100 selection:bg-orange-500/30 selection:text-orange-200 ${className ?? ""}`}
      data-screen="marketing-welcome"
    >
      <Navbar />

      <main>
        <Hero />
        <SocialProof />
        <IndustryProblem />
        <PillarsOverview />
        <InteractiveSandbox />
        <RoiCalculator />
        <Mentors />
        <Testimonials />
        <Pricing />
        <FaqSection />
        <CtaSection />
      </main>

      <Footer />
    </div>
  );
}
