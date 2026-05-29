"use client";

import { useEffect, useState } from "react";

import {
  apiHealthLabel,
  fetchApiHealthState,
  getDeployBadgeLabel,
  type ApiHealthState,
} from "@/lib/deploy-info";

const HEALTH_POLL_MS = 60_000;

function healthDotClass(state: ApiHealthState): string {
  switch (state) {
    case "ok":
      return "bg-success";
    case "degraded":
      return "bg-warning";
    case "unreachable":
      return "bg-text-muted";
    default:
      return "bg-text-muted animate-pulse";
  }
}

export function DeployBadge() {
  const [health, setHealth] = useState<ApiHealthState>("loading");
  const label = getDeployBadgeLabel();

  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      const next = await fetchApiHealthState();
      if (!cancelled) setHealth(next);
    };

    void check();
    const timer = setInterval(() => void check(), HEALTH_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  return (
    <footer
      className="pointer-events-auto fixed inset-x-0 bottom-0 z-auto flex items-center justify-center gap-2 border-t border-border bg-surface/90 px-3 py-1.5 text-xs text-text-muted backdrop-blur-sm"
      data-testid="deploy-badge"
      aria-label={`${label}. ${apiHealthLabel(health)}`}
    >
      <span
        className={`h-2 w-2 shrink-0 rounded-full ${healthDotClass(health)}`}
        title={apiHealthLabel(health)}
        aria-hidden
      />
      <span className="font-mono">{label}</span>
      <span className="hidden sm:inline text-text-muted">· {apiHealthLabel(health)}</span>
    </footer>
  );
}
