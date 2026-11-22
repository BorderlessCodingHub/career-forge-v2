"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { FileText } from "lucide-react";
import { useTranslations } from "next-intl";

import { SignOutButton } from "@/components/auth/SignOutButton";
import { FeedbackLink } from "@/components/feedback/FeedbackLink";
import { LocaleSwitch } from "@/components/i18n/LocaleSwitch";
import { FundamentalsLink } from "@/components/layout/FundamentalsLink";

export const learnerTopbarClass =
  "relative z-10 flex flex-nowrap items-center justify-between gap-6 overflow-hidden border-b border-border bg-bg-sidebar px-5 py-3";

type LearnerTopbarActionsProps = {
  fundamentals?: boolean;
  feedback?: boolean;
  mentorReport?: boolean;
  signOut?: boolean;
  children?: ReactNode;
};

export function LearnerTopbarActions({
  fundamentals = false,
  feedback = false,
  mentorReport = false,
  signOut = false,
  children,
}: LearnerTopbarActionsProps) {
  const t = useTranslations("chrome");

  return (
    <div className="flex shrink-0 items-center gap-5">
      {fundamentals || feedback ? (
        <div className="flex items-center gap-4">
          {fundamentals ? <FundamentalsLink appearance="quiet" /> : null}
          {feedback ? <FeedbackLink appearance="quiet" /> : null}
        </div>
      ) : null}
      {mentorReport ? (
        <Link
          href="/report"
          className="inline-flex h-9 items-center gap-2 rounded-md bg-accent px-3 text-xs font-medium text-white transition hover:opacity-90"
          data-testid="mentor-report-link"
        >
          <FileText className="h-4 w-4" aria-hidden />
          <span>{t("mentorReport")}</span>
        </Link>
      ) : null}
      <div className="flex items-center gap-3 border-l border-border pl-4">
        <LocaleSwitch />
        {signOut ? <SignOutButton appearance="quiet" /> : null}
        {children}
      </div>
    </div>
  );
}
