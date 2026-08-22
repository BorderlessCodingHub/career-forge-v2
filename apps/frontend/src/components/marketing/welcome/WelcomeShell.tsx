"use client";

import { useState } from "react";

import { ApplicationModal } from "./ApplicationModal";
import { CtaSection } from "./CtaSection";
import { CurriculumRoadmap } from "./CurriculumRoadmap";
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
import { StrategyCallModal } from "./StrategyCallModal";
import { SyllabusModal } from "./SyllabusModal";
import { Testimonials } from "./Testimonials";

import "./welcome.css";

type WelcomeShellProps = {
  className?: string;
};

export function WelcomeShell({ className }: WelcomeShellProps) {
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [isSyllabusModalOpen, setIsSyllabusModalOpen] = useState(false);
  const [isStrategyModalOpen, setIsStrategyModalOpen] = useState(false);

  return (
    <div
      className={`welcome-premium min-h-screen bg-slate-950 text-slate-100 selection:bg-orange-500/30 selection:text-orange-200 ${className ?? ""}`}
      data-screen="marketing-welcome"
    >
      <Navbar
        onOpenApplyModal={() => setIsApplyModalOpen(true)}
        onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
        onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
      />

      <main>
        <Hero
          onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
          onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
        />

        <SocialProof />

        <IndustryProblem onOpenApplyModal={() => setIsApplyModalOpen(true)} />

        <PillarsOverview
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
          onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
        />

        <InteractiveSandbox />

        <CurriculumRoadmap
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
          onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
        />

        <RoiCalculator onOpenApplyModal={() => setIsApplyModalOpen(true)} />

        <Mentors />

        <Testimonials />

        <Pricing
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
          onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
          onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
        />

        <FaqSection onOpenStrategyModal={() => setIsStrategyModalOpen(true)} />

        <CtaSection onOpenStrategyModal={() => setIsStrategyModalOpen(true)} />
      </main>

      <Footer
        onOpenApplyModal={() => setIsApplyModalOpen(true)}
        onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
      />

      <ApplicationModal
        isOpen={isApplyModalOpen}
        onClose={() => setIsApplyModalOpen(false)}
      />

      <SyllabusModal
        isOpen={isSyllabusModalOpen}
        onClose={() => setIsSyllabusModalOpen(false)}
      />

      <StrategyCallModal
        isOpen={isStrategyModalOpen}
        onClose={() => setIsStrategyModalOpen(false)}
      />
    </div>
  );
}
