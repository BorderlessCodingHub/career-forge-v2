import Link from "next/link";

import { BrandMark } from "@/components/ui/BrandMark";

const FEATURES = [
  {
    title: "Adaptive diagnosis",
    body: "A short multi-turn interview maps where you are — skills, constraints, and proof — before any roadmap is forged.",
  },
  {
    title: "Live Roadmap Forge",
    body: "Watch your trail take shape in real time: streaming steps, not a static PDF syllabus.",
  },
  {
    title: "Validate mastery",
    body: "AI-backed checks confirm what you can actually do. The roadmap reacts when evidence lands.",
  },
] as const;

const SHOWCASE_STEPS = [
  { label: "Diagnose", detail: "CTRR-style interview → profile" },
  { label: "Forge", detail: "Live SSE trail for your goal" },
  { label: "Validate", detail: "Mastery loops → roadmap updates" },
] as const;

const BENEFITS = [
  {
    title: "Built for BASE & PSP",
    body: "Calibrated for Borderless learners — from early LLM track switchers to deep practitioners.",
  },
  {
    title: "Four LLM goals",
    body: "RAG engineer, agent engineer, LLM evals, and fine-tuning — one focused funnel.",
  },
  {
    title: "Evidence over years of XP",
    body: "Passage is about demonstrated fit, not a résumé year count.",
  },
] as const;

const FAQ = [
  {
    q: "What is Career Forge?",
    a: "An adaptive learning system: diagnose your starting point, forge a live skill trail, and validate mastery so the roadmap stays honest.",
  },
  {
    q: "Who is it for?",
    a: "BASE and PSP learners at Borderless — people building LLM-era skills across the experience spectrum.",
  },
  {
    q: "How do I start?",
    a: "Click Start. You enter the product as a guest, pick a goal, and begin the diagnosis. No platform login required for this pilot phase.",
  },
] as const;

function StartCta({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`inline-flex items-center justify-center rounded-md bg-accent px-5 py-2.5 text-sm font-medium text-white transition hover:opacity-90 ${className}`}
      data-testid="welcome-cta-start"
    >
      Start
    </Link>
  );
}

export function WelcomeLanding() {
  return (
    <div
      className="min-h-screen bg-bg text-text-primary"
      data-screen="marketing-welcome"
    >
      <header className="sticky top-0 z-40 border-b border-border-soft/80 bg-bg/90 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
          <Link
            href="/welcome"
            className="flex items-center gap-2.5"
            aria-label="Career Forge welcome"
          >
            <BrandMark size={28} />
            <span className="text-sm font-medium tracking-tight text-text-primary">
              Career Forge
            </span>
          </Link>
          <StartCta />
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden border-b border-border-soft">
          <div
            className="pointer-events-none absolute inset-0 bg-dot-grid bg-dots opacity-60"
            aria-hidden
          />
          <div
            className="pointer-events-none absolute -top-24 left-1/2 h-64 w-[36rem] -translate-x-1/2 rounded-full bg-accent/20 blur-3xl"
            aria-hidden
          />
          <div className="relative mx-auto max-w-3xl px-4 pb-16 pt-16 text-center sm:px-6 sm:pb-20 sm:pt-20">
            <p className="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-accent-mint">
              Borderless Labs
            </p>
            <h1 className="text-balance text-3xl font-semibold tracking-tight text-text-primary sm:text-4xl md:text-[2.75rem] md:leading-tight">
              Diagnose. Forge live. Validate mastery.
            </h1>
            <p className="mx-auto mt-5 max-w-xl text-pretty text-base text-text-secondary sm:text-lg">
              Career Forge builds an adaptive skill path for BASE and PSP
              learners — from interview to live trail to evidence that moves the
              roadmap.
            </p>
            <div className="mt-8 flex justify-center">
              <StartCta className="px-6 py-3 text-base" />
            </div>
          </div>
        </section>

        {/* Social proof — honest line only */}
        <section
          className="border-b border-border-soft bg-surface/40 py-6"
          aria-label="Audience"
        >
          <p className="mx-auto max-w-3xl px-4 text-center text-sm text-text-secondary sm:px-6">
            Built for{" "}
            <span className="text-text-primary">Borderless</span>
            {" · "}
            <span className="text-text-primary">BASE</span>
            {" & "}
            <span className="text-text-primary">PSP</span>
            {" "}learners
          </p>
        </section>

        {/* Features */}
        <section className="border-b border-border-soft py-16 sm:py-20">
          <div className="mx-auto max-w-5xl px-4 sm:px-6">
            <h2 className="text-center text-2xl font-semibold tracking-tight">
              How it works
            </h2>
            <p className="mx-auto mt-3 max-w-lg text-center text-sm text-text-secondary">
              One continuous loop — not a course catalog.
            </p>
            <ul className="mt-10 grid gap-6 sm:grid-cols-3">
              {FEATURES.map((f) => (
                <li
                  key={f.title}
                  className="rounded-card border border-border bg-surface p-5"
                >
                  <h3 className="text-base font-medium text-text-primary">
                    {f.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-secondary">
                    {f.body}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* Product showcase */}
        <section className="border-b border-border-soft py-16 sm:py-20">
          <div className="mx-auto max-w-5xl px-4 sm:px-6">
            <h2 className="text-center text-2xl font-semibold tracking-tight">
              The product path
            </h2>
            <p className="mx-auto mt-3 max-w-lg text-center text-sm text-text-secondary">
              Composition of the live flow — diagnosis to forge to validation.
            </p>
            <div className="mx-auto mt-10 max-w-2xl overflow-hidden rounded-card border border-border bg-surface">
              <div className="h-1 w-full bg-brand-ribbon" aria-hidden />
              <ol className="divide-y divide-border">
                {SHOWCASE_STEPS.map((step, i) => (
                  <li
                    key={step.label}
                    className="flex items-start gap-4 px-5 py-4 sm:px-6"
                  >
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/25 text-xs font-semibold text-accent-mint">
                      {i + 1}
                    </span>
                    <div>
                      <p className="font-medium text-text-primary">
                        {step.label}
                      </p>
                      <p className="mt-0.5 text-sm text-text-secondary">
                        {step.detail}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </section>

        {/* Benefits */}
        <section className="border-b border-border-soft py-16 sm:py-20">
          <div className="mx-auto max-w-5xl px-4 sm:px-6">
            <h2 className="text-center text-2xl font-semibold tracking-tight">
              Why it fits
            </h2>
            <ul className="mt-10 grid gap-6 sm:grid-cols-3">
              {BENEFITS.map((b) => (
                <li key={b.title}>
                  <h3 className="text-base font-medium text-text-primary">
                    {b.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-secondary">
                    {b.body}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* FAQ */}
        <section className="border-b border-border-soft py-16 sm:py-20">
          <div className="mx-auto max-w-2xl px-4 sm:px-6">
            <h2 className="text-center text-2xl font-semibold tracking-tight">
              FAQ
            </h2>
            <dl className="mt-10 space-y-6">
              {FAQ.map((item) => (
                <div key={item.q}>
                  <dt className="text-base font-medium text-text-primary">
                    {item.q}
                  </dt>
                  <dd className="mt-2 text-sm leading-relaxed text-text-secondary">
                    {item.a}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-16 sm:py-20">
          <div className="mx-auto max-w-xl px-4 text-center sm:px-6">
            <h2 className="text-2xl font-semibold tracking-tight">
              Ready when you are
            </h2>
            <p className="mt-3 text-sm text-text-secondary">
              Enter the product, pick a goal, and start your diagnosis.
            </p>
            <div className="mt-8 flex justify-center">
              <StartCta className="px-6 py-3 text-base" />
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-border-soft py-8">
        <div className="mx-auto flex max-w-5xl items-center justify-center gap-2 px-4 text-xs text-text-muted sm:px-6">
          <BrandMark size={20} variant="inherit" />
          <span>Career Forge · Borderless Labs</span>
        </div>
      </footer>
    </div>
  );
}
