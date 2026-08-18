import { ForgeProductMock } from "./ForgeProductMock";
import { ScrollReveal } from "./ScrollReveal";
import { StartDiagnosisCta } from "./StartDiagnosisCta";
import { WelcomeVariantShell } from "./WelcomeVariantShell";
import { heroItemStyle } from "./welcome-motion";

const PHASES = [
  {
    when: "Before",
    title: "Start diagnosis prepared",
    body: "A short interview maps skills, constraints, and proof — who’s in the room is you. No roadmap until this is honest.",
  },
  {
    when: "During",
    title: "Give the forge your attention",
    body: "Don’t choose between waiting and guessing. The Live Roadmap Forge streams the path in real time, personal to your goal.",
  },
  {
    when: "After",
    title: "The map stays honest",
    body: "Mastery checks and the next node are ready when evidence lands, so you move on proof — not a static syllabus.",
  },
] as const;

const FEATURES = [
  {
    title: "Humans in the loop, not a catalog",
    body: "Career Forge doesn’t drop a course list. It diagnoses, then forges a roadmap you can watch.",
  },
  {
    title: "Works for four LLM goals",
    body: "RAG engineer, agent engineer, LLM evals, fine-tuning — one funnel, four destinations.",
  },
  {
    title: "Evidence by default",
    body: "Passage is demonstrated fit. Years of XP are not the gate.",
  },
] as const;

export function PlgLanding() {
  return (
    <WelcomeVariantShell
      dataScreen="marketing-welcome-plg"
      homeHref="/welcome/plg"
      ctaTestId="welcome-plg-cta-start"
    >
      <main>
        <section className="border-b border-border-soft px-4 pb-16 pt-12 sm:px-6 sm:pb-20 sm:pt-16">
          <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-2 lg:gap-16">
            <div>
              <p
                className="welcome-hero-item mb-4 text-xs font-medium uppercase tracking-[0.2em] text-accent-mint"
                style={heroItemStyle(0)}
              >
                Borderless Labs
              </p>
              <h1
                className="welcome-hero-item text-balance text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl"
                style={heroItemStyle(1)}
              >
                The adaptive roadmap for BASE &amp; PSP
              </h1>
              <p
                className="welcome-hero-item mt-5 max-w-md text-pretty text-base text-text-secondary sm:text-lg"
                style={heroItemStyle(2)}
              >
                Diagnosis, a live forge, mastery checks. Without a static
                syllabus.
              </p>
              <div className="welcome-hero-item mt-8" style={heroItemStyle(3)}>
                <StartDiagnosisCta
                  className="px-6 py-3 text-base"
                  testId="welcome-plg-cta-hero"
                />
              </div>
            </div>
            <div className="welcome-hero-item" style={heroItemStyle(6)}>
              <ForgeProductMock />
            </div>
          </div>
        </section>

        <section
          className="border-b border-border-soft bg-surface/40 py-6"
          aria-label="Audience"
        >
          <p className="mx-auto max-w-6xl px-4 text-center text-sm text-text-secondary sm:px-6">
            Built for{" "}
            <span className="text-text-primary">Borderless</span>
            {" · "}
            <span className="text-text-primary">BASE</span>
            {" & "}
            <span className="text-text-primary">PSP</span>
            {" "}learners
          </p>
        </section>

        <section className="border-b border-border-soft px-4 py-16 sm:px-6 sm:py-20">
          <div className="mx-auto max-w-6xl">
            <h2 className="max-w-xl text-2xl font-semibold tracking-tight sm:text-3xl">
              Career Forge helps you before, during, and after the forge.
            </h2>
            <ul className="mt-12 grid gap-8 md:grid-cols-3">
              {PHASES.map((phase, i) => (
                <ScrollReveal key={phase.when} as="li" delayIndex={i}>
                  <p className="text-xs font-medium uppercase tracking-[0.18em] text-accent-mint">
                    {phase.when}
                  </p>
                  <h3 className="mt-3 text-base font-medium text-text-primary">
                    {phase.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-secondary">
                    {phase.body}
                  </p>
                </ScrollReveal>
              ))}
            </ul>
          </div>
        </section>

        <section className="border-b border-border-soft px-4 py-16 sm:px-6 sm:py-20">
          <div className="mx-auto max-w-6xl">
            <h2 className="text-2xl font-semibold tracking-tight">
              Works the way the product works
            </h2>
            <ul className="mt-10 grid gap-6 sm:grid-cols-3">
              {FEATURES.map((f, i) => (
                <ScrollReveal key={f.title} as="li" delayIndex={i}>
                  <div className="welcome-card h-full rounded-card border border-border bg-surface p-5">
                    <h3 className="text-base font-medium text-text-primary">
                      {f.title}
                    </h3>
                    <p className="mt-2 text-sm leading-relaxed text-text-secondary">
                      {f.body}
                    </p>
                  </div>
                </ScrollReveal>
              ))}
            </ul>
          </div>
        </section>

        <section className="px-4 py-16 sm:px-6 sm:py-20">
          <div className="mx-auto max-w-xl text-center">
            <h2 className="text-2xl font-semibold tracking-tight">
              Start diagnosis — free for this pilot
            </h2>
            <p className="mt-3 text-sm text-text-secondary">
              Guest access. No checkout. Pick a goal on the next screen.
            </p>
            <div className="mt-8 flex justify-center">
              <StartDiagnosisCta
                className="px-6 py-3 text-base"
                testId="welcome-plg-cta-final"
              />
            </div>
          </div>
        </section>
      </main>
    </WelcomeVariantShell>
  );
}
