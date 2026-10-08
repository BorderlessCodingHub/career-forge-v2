"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

import { Button } from "@/components/ui";
import { IdentityGateShell } from "@/components/auth/IdentityGateShell";
import { PasswordIdentityGate } from "@/components/auth/PasswordIdentityGate";
import {
  OtpEmailOwnedError,
  enterPilot,
  requestOtp,
  verifyOtp,
} from "@/lib/api-client";
import { adoptSession } from "@/lib/user-session";
import type { IdentityMethod, OtpEmailOwnedConflict } from "@/types/contracts";

type OtpPhase =
  | { status: "idle" }
  | { status: "code_sent"; email: string }
  | { status: "verifying" }
  | {
      status: "conflict";
      email: string;
      existing: OtpEmailOwnedConflict["existing"];
    };

type IdentityGateProps = {
  title?: string;
  description?: string;
  method?: IdentityMethod;
  emailOtpRequired?: boolean;
  forgotPasswordUrl?: string;
  signupUrl?: string;
  onVerified: () => void;
};

export function IdentityGate({
  title,
  description,
  method,
  emailOtpRequired = true,
  forgotPasswordUrl = "",
  signupUrl = "",
  onVerified,
}: IdentityGateProps) {
  const t = useTranslations("identity");
  const resolvedMethod =
    method ?? (emailOtpRequired ? "email_otp" : "pilot_enter");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [otpPhase, setOtpPhase] = useState<OtpPhase>({ status: "idle" });
  const [otpBusy, setOtpBusy] = useState(false);
  const [otpError, setOtpError] = useState<string | null>(null);

  if (resolvedMethod === "borderless_password") {
    return (
      <PasswordIdentityGate
        forgotPasswordUrl={forgotPasswordUrl}
        signupUrl={signupUrl}
        onVerified={onVerified}
      />
    );
  }

  const resolvedTitle =
    title ?? (emailOtpRequired ? t("signInWithEmail") : t("pilotEmail"));
  const resolvedDescription =
    description ??
    (emailOtpRequired ? t("otpDescription") : t("pilotDescription"));

  async function handleContinue() {
    const trimmed = email.trim();
    if (!trimmed) {
      setOtpError(t("enterEmailFirst"));
      return;
    }
    setOtpBusy(true);
    setOtpError(null);
    try {
      await enterPilot(trimmed);
      onVerified();
    } catch (err) {
      setOtpError(err instanceof Error ? err.message : t("failedToEnter"));
    } finally {
      setOtpBusy(false);
    }
  }

  async function handleRequestCode() {
    const trimmed = email.trim();
    if (!trimmed) {
      setOtpError(t("enterEmailFirst"));
      return;
    }
    setOtpBusy(true);
    setOtpError(null);
    try {
      await requestOtp(trimmed);
      setOtpPhase({ status: "code_sent", email: trimmed });
    } catch (err) {
      setOtpError(err instanceof Error ? err.message : t("failedToSend"));
    } finally {
      setOtpBusy(false);
    }
  }

  async function handleVerifyCode() {
    if (otpPhase.status !== "code_sent") return;
    const currentEmail = otpPhase.email;
    setOtpBusy(true);
    setOtpError(null);
    setOtpPhase({ status: "verifying" });
    try {
      await verifyOtp(currentEmail, code.trim());
      onVerified();
    } catch (err) {
      if (err instanceof OtpEmailOwnedError) {
        setOtpPhase({
          status: "conflict",
          email: currentEmail,
          existing: err.conflict.existing,
        });
        return;
      }
      setOtpPhase({ status: "code_sent", email: currentEmail });
      setOtpError(err instanceof Error ? err.message : t("verificationFailed"));
    } finally {
      setOtpBusy(false);
    }
  }

  function handleKeepLocal() {
    setOtpPhase({ status: "code_sent", email: email.trim() });
    setOtpError(null);
  }

  function handleSwitchToExisting(existing: OtpEmailOwnedConflict["existing"]) {
    adoptSession(existing.access_token, existing.external_id);
    onVerified();
  }

  return (
    <IdentityGateShell>
      <div className="mx-auto max-w-md rounded-md border border-border bg-surface px-6 py-8">
        <h1 className="text-2xl font-semibold text-text-primary">{resolvedTitle}</h1>
        <p className="mt-2 text-sm text-text-secondary">{resolvedDescription}</p>

        {otpPhase.status === "conflict" ? (
          <div className="mt-6 space-y-3" data-testid="identity-gate-conflict">
            <p className="text-sm text-text-secondary">
              <span className="text-text-primary">{otpPhase.email}</span>{" "}
              {t("alreadyHasAccount")}
            </p>
            <div className="flex flex-col gap-2 sm:flex-row">
              <Button data-testid="identity-gate-keep-local" onClick={handleKeepLocal}>
                {t("keepSession")}
              </Button>
              <Button
                variant="ghost"
                data-testid="identity-gate-switch"
                onClick={() => handleSwitchToExisting(otpPhase.existing)}
              >
                {t("switchAccount")}
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <input
                type="email"
                className="min-w-0 flex-1 rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
                placeholder="you@example.com"
                value={email}
                disabled={otpBusy || otpPhase.status === "code_sent"}
                data-testid="identity-gate-email"
                onChange={(e) => setEmail(e.target.value)}
              />
              {emailOtpRequired ? (
                <Button
                  variant="ghost"
                  data-testid="identity-gate-request"
                  disabled={otpBusy}
                  onClick={() => void handleRequestCode()}
                >
                  {otpBusy && otpPhase.status === "idle"
                    ? t("sending")
                    : otpPhase.status === "code_sent"
                      ? t("resendCode")
                      : t("sendCode")}
                </Button>
              ) : (
                <Button
                  data-testid="identity-gate-continue"
                  disabled={otpBusy}
                  onClick={() => void handleContinue()}
                >
                  {otpBusy ? t("checking") : t("continue")}
                </Button>
              )}
            </div>
            {emailOtpRequired &&
              (otpPhase.status === "code_sent" ||
                otpPhase.status === "verifying") && (
              <div className="space-y-2">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                  <input
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={6}
                    className="min-w-0 flex-1 rounded-md border border-border bg-bg px-3 py-2 text-sm tracking-widest text-text-primary"
                    placeholder={t("codePlaceholder")}
                    value={code}
                    disabled={otpBusy}
                    data-testid="identity-gate-code"
                    onChange={(e) =>
                      setCode(e.target.value.replace(/\D/g, "").slice(0, 6))
                    }
                  />
                  <Button
                    data-testid="identity-gate-verify"
                    disabled={otpBusy || code.trim().length !== 6}
                    onClick={() => void handleVerifyCode()}
                  >
                    {otpBusy ? t("verifying") : t("verify")}
                  </Button>
                </div>
                <button
                  type="button"
                  className="text-sm text-accent underline-offset-2 hover:underline"
                  data-testid="identity-gate-change-email"
                  onClick={() => {
                    setOtpPhase({ status: "idle" });
                    setCode("");
                    setOtpError(null);
                  }}
                >
                  {t("differentEmail")}
                </button>
              </div>
            )}
          </div>
        )}

        {otpError ? (
          <p className="mt-3 text-sm text-red-400" data-testid="identity-gate-error">
            {otpError}
          </p>
        ) : null}
      </div>
    </IdentityGateShell>
  );
}
