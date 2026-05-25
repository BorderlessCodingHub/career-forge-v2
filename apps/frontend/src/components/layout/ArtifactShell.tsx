import type { HTMLAttributes, ReactNode } from "react";

import { DemoModeToggle } from "@/components/layout/DemoModeToggle";

type ArtifactShellProps = HTMLAttributes<HTMLDivElement> & {
  trackName?: string;
  children: ReactNode;
};

export function ArtifactShell({
  trackName = "Backend Developer",
  className = "",
  children,
  ...props
}: ArtifactShellProps) {
  return (
    <div className={`flex min-h-screen flex-col bg-bg ${className}`} data-mode="artifact" {...props}>
      <header
        className="flex items-center justify-between border-b border-border bg-bg-sidebar px-6 py-4"
        data-testid="artifact-topbar"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/20 text-sm font-semibold text-accent">
            CF
          </div>
          <div>
            <p className="text-sm font-semibold text-text-primary">Career Forge</p>
            <p className="text-xs text-text-muted">Trilha personalizada</p>
          </div>
        </div>
        <DemoModeToggle compact />
        <div className="text-right">
          <p className="text-[10px] uppercase tracking-widest text-text-muted">Sua trilha</p>
          <p className="text-sm font-medium text-text-primary">{trackName}</p>
        </div>
      </header>
      <div className="flex-1">{children}</div>
    </div>
  );
}
