"use client";

import { type ReactNode, useCallback, useEffect, useState } from "react";

import { IdentityGate } from "@/components/auth/IdentityGate";
import { checkAuthSession, getIdentityMode } from "@/lib/api-client";
import { getAccessToken } from "@/lib/user-session";
import { hasEmailProvider } from "@/lib/jwt";

type ProductEntryGateProps = {
  children: ReactNode;
};

type GateState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "gate"; emailOtpRequired: boolean }
  | { status: "in" };

export function ProductEntryGate({ children }: ProductEntryGateProps) {
  const [state, setState] = useState<GateState>({ status: "loading" });

  const resolveGate = useCallback(async () => {
    try {
      const mode = await getIdentityMode();
      if (!hasEmailProvider(getAccessToken())) {
        setState({ status: "gate", emailOtpRequired: mode.email_otp_required });
        return;
      }
      if (mode.email_otp_required) {
        setState({ status: "in" });
        return;
      }
      const allowed = await checkAuthSession();
      if (!allowed) {
        setState({ status: "gate", emailOtpRequired: false });
        return;
      }
      setState({ status: "in" });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Cannot reach identity service.";
      setState({ status: "error", message });
    }
  }, []);

  useEffect(() => {
    void resolveGate();
  }, [resolveGate]);

  const handleVerified = useCallback(() => {
    setState({ status: "in" });
  }, []);

  if (state.status === "loading") {
    return (
      <main className="min-h-screen grid-dots flex items-center justify-center p-8">
        <p className="text-text-secondary" data-testid="product-entry-hydrating">
          Loading…
        </p>
      </main>
    );
  }

  if (state.status === "error") {
    return (
      <main className="min-h-screen grid-dots flex items-center justify-center p-8">
        <p className="text-sm text-red-400" data-testid="product-entry-error">
          {state.message}
        </p>
      </main>
    );
  }

  if (state.status === "gate") {
    return (
      <IdentityGate
        emailOtpRequired={state.emailOtpRequired}
        onVerified={handleVerified}
      />
    );
  }

  return <>{children}</>;
}
