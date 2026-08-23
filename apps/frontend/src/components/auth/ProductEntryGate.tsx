"use client";

import { type ReactNode, useCallback, useState } from "react";

import { IdentityGate } from "@/components/auth/IdentityGate";
import { getAccessToken } from "@/lib/user-session";
import { hasEmailProvider } from "@/lib/jwt";

type ProductEntryGateProps = {
  children: ReactNode;
};

export function ProductEntryGate({ children }: ProductEntryGateProps) {
  const [verified, setVerified] = useState(() =>
    hasEmailProvider(getAccessToken()),
  );

  const handleVerified = useCallback(() => {
    setVerified(true);
  }, []);

  if (!verified) {
    return <IdentityGate onVerified={handleVerified} />;
  }

  return <>{children}</>;
}
