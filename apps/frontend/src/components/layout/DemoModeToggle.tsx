"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { getDemoAna } from "@/lib/api-client";
import { clearAdaptiveSession } from "@/lib/adaptive-session";
import { clearForgeSession } from "@/lib/forge-session";
import { clearOnboardingSession, setStoredDiagnosis } from "@/lib/onboarding-session";
import {
  getUserMode,
  isDemoMode,
  setDemoMode,
  setNewUserMode,
  type UserMode,
} from "@/lib/user-session";

type DemoModeToggleProps = {
  className?: string;
  compact?: boolean;
};

export function DemoModeToggle({ className = "", compact = false }: DemoModeToggleProps) {
  const router = useRouter();
  const [mode, setMode] = useState<UserMode>("demo");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setMode(getUserMode());
  }, []);

  const activateDemo = useCallback(async () => {
    setBusy(true);
    try {
      setDemoMode();
      clearOnboardingSession();
      clearForgeSession();
      clearAdaptiveSession();
      const bundle = await getDemoAna();
      setStoredDiagnosis(bundle.diagnosis);
      setMode("demo");
      router.push("/roadmap?node=rest");
    } finally {
      setBusy(false);
    }
  }, [router]);

  const activateNewUser = useCallback(() => {
    setBusy(true);
    try {
      setNewUserMode();
      clearOnboardingSession();
      clearForgeSession();
      clearAdaptiveSession();
      setMode("new");
      router.push("/");
    } finally {
      setBusy(false);
    }
  }, [router]);

  return (
    <div
      className={`inline-flex items-center rounded-full border border-border bg-surface p-1 ${className}`}
      data-testid="demo-mode-toggle"
      role="group"
      aria-label="Modo demo ou novo usuário"
    >
      <button
        type="button"
        data-testid="demo-mode-ana"
        disabled={busy}
        onClick={() => void activateDemo()}
        className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
          mode === "demo"
            ? "bg-accent text-white shadow-sm"
            : "text-text-secondary hover:text-text-primary"
        } ${compact ? "px-2.5" : ""}`}
      >
        Demo Ana
      </button>
      <button
        type="button"
        data-testid="demo-mode-new"
        disabled={busy}
        onClick={activateNewUser}
        className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
          mode === "new"
            ? "bg-accent text-white shadow-sm"
            : "text-text-secondary hover:text-text-primary"
        } ${compact ? "px-2.5" : ""}`}
      >
        Novo usuário
      </button>
      {!compact && isDemoMode() && (
        <span className="ml-2 hidden text-[10px] uppercase tracking-widest text-text-muted sm:inline">
          pitch 7 min
        </span>
      )}
    </div>
  );
}
