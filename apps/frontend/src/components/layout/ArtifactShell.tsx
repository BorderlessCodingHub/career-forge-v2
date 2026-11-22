"use client";

import type { HTMLAttributes, ReactNode } from "react";
import Link from "next/link";
import { FileText } from "lucide-react";
import { useTranslations } from "next-intl";

import { SignOutButton } from "@/components/auth/SignOutButton";
import { FeedbackLink } from "@/components/feedback/FeedbackLink";
import { LocaleSwitch } from "@/components/i18n/LocaleSwitch";
import { FundamentalsLink } from "@/components/layout/FundamentalsLink";
import { BrandLockup } from "@/components/ui/BrandLockup";

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
      <header
        className="flex flex-nowrap items-center justify-between gap-6 overflow-hidden border-b border-border bg-bg-sidebar px-5 py-3"
        data-testid="artifact-topbar"
      >
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

        <div className="flex shrink-0 items-center gap-5">
          <div className="flex items-center gap-4">
            <FundamentalsLink appearance="quiet" />
            <FeedbackLink appearance="quiet" />
          </div>
          <Link
            href="/report"
            className="inline-flex h-9 items-center gap-2 rounded-md bg-accent px-3 text-xs font-medium text-white transition hover:opacity-90"
            data-testid="mentor-report-link"
          >
            <FileText className="h-4 w-4" aria-hidden />
            <span>{t("mentorReport")}</span>
          </Link>
          <div className="flex items-center gap-3 border-l border-border pl-4">
            <LocaleSwitch />
            <SignOutButton appearance="quiet" />
          </div>
        </div>
      </header>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
