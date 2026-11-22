"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { useTranslations } from "next-intl";

import { BrandLockup } from "@/components/ui/BrandLockup";

import { learnerTopbarClass, LearnerTopbarActions } from "./LearnerTopbarActions";

type ArtifactShellProps = HTMLAttributes<HTMLDivElement> & {
  trackName?: string;
  children: ReactNode;
};

export function ArtifactShell({
  trackName,
  className = "",
  children,
  ...props
}: ArtifactShellProps) {
  const t = useTranslations("chrome");
  const trail = trackName?.trim() || t("loadingTrail");

  return (
    <div className={`flex min-h-screen flex-col bg-bg ${className}`} data-mode="artifact" {...props}>
      <header className={learnerTopbarClass} data-testid="artifact-topbar">
        <div className="flex min-w-0 items-center gap-4">
          <BrandLockup markSize={28} className="shrink-0" />
          <div className="h-8 w-px shrink-0 bg-border" aria-hidden />
          <div className="min-w-0">
            <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-text-muted">
              {t("yourTrail")}
            </p>
            <p className="truncate text-lg font-semibold text-text-primary" title={trail}>
              {trail}
            </p>
          </div>
        </div>

        <LearnerTopbarActions fundamentals feedback mentorReport signOut />
      </header>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
