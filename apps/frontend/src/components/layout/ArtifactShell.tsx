"use client";

import type { HTMLAttributes, ReactNode } from "react";
import Link from "next/link";
import { FileText } from "lucide-react";

import { BrandMark } from "@/components/ui/BrandMark";
import { SignOutButton } from "@/components/auth/SignOutButton";

const topbarActionClass =
  "inline-flex h-9 items-center gap-2 rounded-md border border-border px-3 text-xs font-medium text-text-secondary transition hover:border-accent/40 hover:bg-surface hover:text-text-primary";

const topbarActionIconSlotClass =
  "flex h-7 w-7 shrink-0 items-center justify-center";

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
  return (
    <div className={`flex min-h-screen flex-col bg-bg ${className}`} data-mode="artifact" {...props}>
      <header
        className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-bg-sidebar px-6 py-4"
        data-testid="artifact-topbar"
      >
        <div className="flex items-center gap-3">
          <BrandMark size={36} className="h-9 w-auto" />
          <div>
            <p className="text-sm font-semibold text-text-primary">Career Forge</p>
            <p className="text-xs text-text-muted">Personalized trail</p>
          </div>
        </div>

        <div className="flex flex-wrap items-end justify-end gap-2 sm:gap-3">
          <SignOutButton />
          <Link href="/report" className={topbarActionClass} data-testid="mentor-report-link">
            <span className={topbarActionIconSlotClass} aria-hidden>
              <FileText className="h-4 w-4" />
            </span>
            <span>Mentor report</span>
          </Link>
          <div className="text-right">
            <p className="text-[10px] uppercase tracking-widest text-text-muted">Your trail</p>
            <p className="text-sm font-medium text-text-primary">
              {trackName ?? "Loading trail…"}
            </p>
          </div>
        </div>
      </header>
      <div className="flex-1">{children}</div>
    </div>
  );
}
