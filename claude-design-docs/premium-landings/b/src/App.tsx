import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { SocialProof } from './components/SocialProof';
import { IndustryProblem } from './components/IndustryProblem';
import { PillarsOverview } from './components/PillarsOverview';
import { InteractiveSandbox } from './components/InteractiveSandbox';
import { CurriculumRoadmap } from './components/CurriculumRoadmap';
import { RoiCalculator } from './components/RoiCalculator';
import { Mentors } from './components/Mentors';
import { Testimonials } from './components/Testimonials';
import { Pricing } from './components/Pricing';
import { FaqSection } from './components/FaqSection';
import { CtaSection } from './components/CtaSection';
import { Footer } from './components/Footer';

import { ApplicationModal } from './components/ApplicationModal';
import { SyllabusModal } from './components/SyllabusModal';
import { StrategyCallModal } from './components/StrategyCallModal';

export function App() {
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [isSyllabusModalOpen, setIsSyllabusModalOpen] = useState(false);
  const [isStrategyModalOpen, setIsStrategyModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-orange-500/30 selection:text-orange-200">
      {/* Sticky Glass Navbar */}
      <Navbar
        onOpenApplyModal={() => setIsApplyModalOpen(true)}
        onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
        onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
      />

      {/* Main Content Sections */}
      <main>
        {/* 1. Hero Section with Interactive Code Terminal Switcher */}
        <Hero
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
          onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
          onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
        />

        {/* 2. Social Proof & Ticker Feed */}
        <SocialProof />

        {/* 3. Industry Problem / Developer Gap Comparison */}
        <IndustryProblem
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
        />

        {/* 4. Deep Dive into the 4 Core Pillars */}
        <PillarsOverview
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
          onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
        />

        {/* 5. Live Interactive Sandbox Playground */}
        <InteractiveSandbox />

        {/* 6. 12-Week Curriculum Roadmap & Lab Reviews */}
        <CurriculumRoadmap
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
          onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
        />

        {/* 7. Compensation & ROI Salary Calculator */}
        <RoiCalculator
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
        />

        {/* 8. Lead Instructors & Ex-Labs Team */}
        <Mentors />

        {/* 9. Verified Alumni Success Stories */}
        <Testimonials />

        {/* 10. Transparent Pricing & Scholarship Options */}
        <Pricing
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
          onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
          onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
        />

        {/* 11. Searchable FAQ Section */}
        <FaqSection
          onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
        />

        {/* 12. Urgency CTA Banner */}
        <CtaSection
          onOpenApplyModal={() => setIsApplyModalOpen(true)}
          onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
        />
      </main>

      {/* Footer */}
      <Footer
        onOpenApplyModal={() => setIsApplyModalOpen(true)}
        onOpenSyllabusModal={() => setIsSyllabusModalOpen(true)}
      />

      {/* Modals */}
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

export default App;
