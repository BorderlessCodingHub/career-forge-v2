"use client";

import { type ReactNode, useCallback, useEffect, useState } from "react";

import { IdentityGate } from "@/components/auth/IdentityGate";
import { getAccessToken } from "@/lib/user-session";
import { hasEmailProvider } from "@/lib/jwt";

type ProductEntryGateProps = {
  children: ReactNode;
};

export function ProductEntryGate({ children }: ProductEntryGateProps) {
  // null until mounted — avoids SSR/client mismatch from localStorage reads.
  const [verified, setVerified] = useState<boolean | null>(null);

  useEffect(() => {
    setVerified(hasEmailProvider(getAccessToken()));
  }, []);

  const handleVerified = useCallback(() => {
    setVerified(true);
  }, []);

  if (verified === null) {
    return (
      <main className="min-h-screen grid-dots flex items-center justify-center p-8">
        <p className="text-text-secondary" data-testid="product-entry-hydrating">
          Loading…
        </p>
      </main>
    );
  }

  if (!verified) {
    return <IdentityGate onVerified={handleVerified} />;
  }

  return <>{children}</>;
}
