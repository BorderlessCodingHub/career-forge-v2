"use client";

import { type ReactNode, useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { IdentityGate } from "@/components/auth/IdentityGate";
import { useSyncStoredLocale } from "@/components/i18n/useSyncStoredLocale";
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
      borderlessOAuth: boolean;
    }
  | { status: "in" };

export function ProductEntryGate({ children }: ProductEntryGateProps) {
  const t = useTranslations("product");
  const [state, setState] = useState<GateState>({ status: "loading" });
  useSyncStoredLocale(state.status === "in");

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
          borderlessOAuth: Boolean(mode.borderless_oauth),
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
          borderlessOAuth: Boolean(mode.borderless_oauth),
        });
        return;
      }
      setState({ status: "in" });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : t("identityUnreachable");
      setState({ status: "error", message });
    }
  }, [t]);

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
          {t("loading")}
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
        borderlessOAuth={state.borderlessOAuth}
        onVerified={handleVerified}
      />
    );
  }

  return <>{children}</>;
}
