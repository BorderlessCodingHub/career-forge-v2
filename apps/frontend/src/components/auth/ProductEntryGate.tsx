"use client";

import { type ReactNode, useCallback, useEffect, useState } from "react";

import { IdentityGate } from "@/components/auth/IdentityGate";
import { checkAuthSession, getIdentityMode } from "@/lib/api-client";
import { getAccessToken } from "@/lib/user-session";
import { hasEmailProvider } from "@/lib/jwt";
import type { IdentityMethod } from "@/types/contracts";

type ProductEntryGateProps = {
  children: ReactNode;
};

type GateState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | {
      status: "gate";
      method: IdentityMethod;
      emailOtpRequired: boolean;
      signupUrl: string;
      forgotPasswordUrl: string;
    }
  | { status: "in" };

export function ProductEntryGate({ children }: ProductEntryGateProps) {
  const [state, setState] = useState<GateState>({ status: "loading" });

  const resolveGate = useCallback(async () => {
    try {
      const mode = await getIdentityMode();
      const signupUrl = mode.signup_url ?? "";
      const forgotPasswordUrl = mode.forgot_password_url ?? "";
      if (!hasEmailProvider(getAccessToken())) {
        setState({
          status: "gate",
          method: mode.method,
          emailOtpRequired: mode.email_otp_required,
          signupUrl,
          forgotPasswordUrl,
        });
        return;
      }
      if (mode.email_otp_required) {
        setState({ status: "in" });
        return;
      }
      const allowed = await checkAuthSession();
      if (!allowed) {
        setState({
          status: "gate",
          method: mode.method,
          emailOtpRequired: false,
          signupUrl,
          forgotPasswordUrl,
        });
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
        method={state.method}
        emailOtpRequired={state.emailOtpRequired}
        signupUrl={state.signupUrl}
        forgotPasswordUrl={state.forgotPasswordUrl}
        onVerified={handleVerified}
      />
    );
  }

  return <>{children}</>;
}
