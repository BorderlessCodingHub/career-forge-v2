import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";

import { BrandMark } from "@/components/ui/BrandMark";

import { StartDiagnosisCta } from "./StartDiagnosisCta";
import { WELCOME_DURATION_MS, WELCOME_TRANSLATE_PX } from "./welcome-motion";

type WelcomeVariantShellProps = {
  dataScreen: string;
  homeHref: string;
  ctaTestId: string;
  children: ReactNode;
};

export function WelcomeVariantShell({
  dataScreen,
  homeHref,
  ctaTestId,
  children,
}: WelcomeVariantShellProps) {
  return (
    <div
      className="min-h-screen bg-bg text-text-primary"
      data-screen={dataScreen}
      style={
        {
          "--welcome-duration": `${WELCOME_DURATION_MS}ms`,
          "--welcome-translate": `${WELCOME_TRANSLATE_PX}px`,
        } as CSSProperties
      }
    >
      <noscript>
        <style>{`.welcome-reveal{opacity:1!important;transform:none!important}`}</style>
      </noscript>

      <header className="sticky top-0 z-40 border-b border-border-soft/80 bg-bg/90 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
          <Link
            href={homeHref}
            className="flex items-center gap-2.5"
            aria-label="Career Forge"
          >
            <BrandMark size={28} />
            <span className="text-sm font-medium tracking-tight text-text-primary">
              Career Forge
            </span>
          </Link>
          <StartDiagnosisCta testId={ctaTestId} />
        </div>
      </header>

      {children}

      <footer className="border-t border-border-soft py-8">
        <div className="mx-auto flex max-w-5xl items-center justify-center gap-2 px-4 text-xs text-text-muted sm:px-6">
          <BrandMark size={20} variant="inherit" />
          <span>Career Forge · Borderless Labs</span>
        </div>
      </footer>
    </div>
  );
}
