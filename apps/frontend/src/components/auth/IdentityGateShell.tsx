"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useTranslations } from "next-intl";

import { learnerTopbarClass, LearnerTopbarActions } from "@/components/layout/LearnerTopbarActions";
import { BrandLockup } from "@/components/ui/BrandLockup";

type IdentityGateShellProps = {
  children: ReactNode;
  /** Optional data-screen for agent-verify / product docs (password path). */
  screen?: string;
};

export function IdentityGateShell({ children, screen }: IdentityGateShellProps) {
  const t = useTranslations("chrome");
  return (
    <main
      className="relative min-h-screen overflow-hidden bg-slate-950"
      data-testid="identity-gate"
      {...(screen ? { "data-screen": screen } : {})}
    >
      <div className="pointer-events-none absolute inset-0 hero-dots opacity-30" />
      <div className="pointer-events-none absolute top-1/4 left-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-tr from-orange-600/15 via-indigo-600/20 to-purple-600/15 blur-[120px]" />
      <div className="pointer-events-none absolute top-10 right-10 h-96 w-96 rounded-full bg-cyan-500/10 blur-[100px]" />

      <header className={learnerTopbarClass} data-testid="identity-gate-topbar">
        <BrandLockup markSize={28} className="shrink-0" />
        <LearnerTopbarActions>
          <Link
            href="/welcome"
            className="text-sm font-medium text-text-secondary transition hover:text-text-primary"
            data-testid="identity-gate-back-welcome"
          >
            {t("backToWelcome")}
          </Link>
        </LearnerTopbarActions>
      </header>

      <div className="relative z-10 px-4 py-10">{children}</div>
    </main>
  );
}
