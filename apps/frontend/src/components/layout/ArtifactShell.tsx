import type { HTMLAttributes, ReactNode } from "react";
import Link from "next/link";

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
        className="flex items-center justify-between border-b border-border bg-bg-sidebar px-6 py-4"
        data-testid="artifact-topbar"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-accent/20 text-sm font-semibold text-accent">
            CF
          </div>
          <div>
            <p className="text-sm font-semibold text-text-primary">Career Forge</p>
            <p className="text-xs text-text-muted">Trilha personalizada</p>
          </div>
        </div>
        <Link
          href="/report"
          className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-text-secondary transition hover:border-accent hover:text-accent"
          data-testid="mentor-report-link"
        >
          Relatório mentor
        </Link>
        <div className="text-right">
          <p className="text-[10px] uppercase tracking-widest text-text-muted">Sua trilha</p>
          <p className="text-sm font-medium text-text-primary">
            {trackName ?? "Carregando trilha…"}
          </p>
        </div>
      </header>
      <div className="flex-1">{children}</div>
    </div>
  );
}
