"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type ArtifactChromeState = {
  trailProgressPct?: number | null;
};

type ArtifactChromeContextValue = ArtifactChromeState & {
  setChrome: (patch: Partial<ArtifactChromeState>) => void;
  clearChrome: () => void;
};

const ArtifactChromeContext = createContext<ArtifactChromeContextValue | null>(null);

export function ArtifactChromeProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ArtifactChromeState>({});

  const setChrome = useCallback((patch: Partial<ArtifactChromeState>) => {
    setState((prev) => ({ ...prev, ...patch }));
  }, []);

  const clearChrome = useCallback(() => {
    setState({});
  }, []);

  const value = useMemo(
    () => ({ ...state, setChrome, clearChrome }),
    [state, setChrome, clearChrome],
  );

  return (
    <ArtifactChromeContext.Provider value={value}>{children}</ArtifactChromeContext.Provider>
  );
}

export function useArtifactChrome() {
  const ctx = useContext(ArtifactChromeContext);
  if (!ctx) {
    throw new Error("useArtifactChrome must be used within ArtifactChromeProvider");
  }
  return ctx;
}

export function useArtifactChromeOptional() {
  return useContext(ArtifactChromeContext);
}
