"use client";

import { useEffect, useState, type ReactNode } from "react";

import { getRoadmap } from "@/lib/api-client";
import { getStoredDiagnosis } from "@/lib/onboarding-session";

import { ArtifactChromeProvider } from "./ArtifactChromeContext";
import { ArtifactShell } from "./ArtifactShell";

function readTrackNameFromSession(): string | undefined {
  return getStoredDiagnosis()?.profile.label ?? undefined;
}

export function ArtifactShellLayout({ children }: { children: ReactNode }) {
  const [trackName, setTrackName] = useState<string | undefined>(() =>
    typeof window !== "undefined" ? readTrackNameFromSession() : undefined,
  );

  useEffect(() => {
    const fromDiagnosis = readTrackNameFromSession();
    if (fromDiagnosis) {
      setTrackName(fromDiagnosis);
      return;
    }

    let cancelled = false;
    void getRoadmap()
      .then((roadmap) => {
        if (!cancelled) setTrackName(roadmap.track.title);
      })
      .catch(() => {
        /* keep placeholder — roadmap may not exist yet */
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <ArtifactChromeProvider>
      <ArtifactShell trackName={trackName}>{children}</ArtifactShell>
    </ArtifactChromeProvider>
  );
}
