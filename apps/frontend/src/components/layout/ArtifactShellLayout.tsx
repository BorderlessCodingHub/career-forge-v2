"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import { getRoadmap } from "@/lib/api-client";
import { getStoredDiagnosis } from "@/lib/onboarding-session";
import { shouldShowArtifactShell } from "@/lib/product-chrome";
import { hasEmailIdentity } from "@/lib/user-session";

import { ArtifactShell } from "./ArtifactShell";

function readTrackNameFromSession(): string | undefined {
  return getStoredDiagnosis()?.profile.label ?? undefined;
}

export function ArtifactShellLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [signedIn, setSignedIn] = useState(false);
  const [trackName, setTrackName] = useState<string | undefined>(() =>
    typeof window !== "undefined" ? readTrackNameFromSession() : undefined,
  );

  useEffect(() => {
    setSignedIn(hasEmailIdentity());
  }, []);

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

  if (!shouldShowArtifactShell(pathname, signedIn)) {
    return <>{children}</>;
  }

  return <ArtifactShell trackName={trackName}>{children}</ArtifactShell>;
}
