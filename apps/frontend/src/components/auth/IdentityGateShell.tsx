"use client";

import Link from "next/link";
import type { ReactNode } from "react";

import { BrandLockup } from "@/components/ui/BrandLockup";

type IdentityGateShellProps = {
  children: ReactNode;
  /** Optional data-screen for agent-verify / product docs (password path). */
  screen?: string;
};

export function IdentityGateShell({ children, screen }: IdentityGateShellProps) {
  return (
    <main
      className="relative min-h-screen overflow-hidden bg-slate-950"
      data-testid="identity-gate"
      {...(screen ? { "data-screen": screen } : {})}
    >
      <div className="pointer-events-none absolute inset-0 hero-dots opacity-30" />
      <div className="pointer-events-none absolute top-1/4 left-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-tr from-orange-600/15 via-indigo-600/20 to-purple-600/15 blur-[120px]" />
      <div className="pointer-events-none absolute top-10 right-10 h-96 w-96 rounded-full bg-cyan-500/10 blur-[100px]" />

      <header
        className="relative z-10 flex flex-wrap items-center justify-between gap-3 border-b border-border bg-bg-sidebar px-6 py-4"
        data-testid="identity-gate-topbar"
      >
        <BrandLockup />
        <Link
          href="/welcome"
          className="text-sm text-text-secondary underline-offset-2 hover:underline"
          data-testid="identity-gate-back-welcome"
        >
          Back to Welcome
        </Link>
      </header>

      <div className="relative z-10 px-4 py-10">{children}</div>
    </main>
  );
}
