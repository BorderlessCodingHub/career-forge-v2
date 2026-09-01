"use client";

import { useState } from "react";

import { Button } from "@/components/ui";
import { BrandLockup } from "@/components/ui/BrandLockup";
import {
  OtpEmailOwnedError,
  enterPilot,
  requestOtp,
  verifyOtp,
} from "@/lib/api-client";
import { adoptSession } from "@/lib/user-session";
import type { OtpEmailOwnedConflict } from "@/types/contracts";

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
  emailOtpRequired?: boolean;
  onVerified: () => void;
};

export function IdentityGate({
  title,
  description,
  emailOtpRequired = true,
  onVerified,
}: IdentityGateProps) {
  const resolvedTitle =
    title ?? (emailOtpRequired ? "Sign in with email" : "Enter your pilot email");
  const resolvedDescription =
    description ??
    (emailOtpRequired
      ? "Enter your email to continue. We send a 6-digit code (check backend logs in local dev)."
      : "Enter the email on the pilot list to continue.");

  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [otpPhase, setOtpPhase] = useState<OtpPhase>({ status: "idle" });
  const [otpBusy, setOtpBusy] = useState(false);
  const [otpError, setOtpError] = useState<string | null>(null);

  async function handleContinue() {
    const trimmed = email.trim();
    if (!trimmed) {
      setOtpError("Enter your email first.");
      return;
    }
    setOtpBusy(true);
    setOtpError(null);
    try {
      await enterPilot(trimmed);
      onVerified();
    } catch (err) {
      setOtpError(err instanceof Error ? err.message : "Failed to enter.");
    } finally {
      setOtpBusy(false);
    }
  }

  async function handleRequestCode() {
    const trimmed = email.trim();
    if (!trimmed) {
      setOtpError("Enter your email first.");
      return;
    }
    setOtpBusy(true);
    setOtpError(null);
    try {
      await requestOtp(trimmed);
      setOtpPhase({ status: "code_sent", email: trimmed });
    } catch (err) {
      setOtpError(err instanceof Error ? err.message : "Failed to send code.");
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
      setOtpError(err instanceof Error ? err.message : "Verification failed.");
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
    <main
      className="min-h-screen grid-dots px-4 py-10"
      data-testid="identity-gate"
    >
      <div className="mx-auto max-w-md rounded-md border border-border bg-surface px-6 py-8">
        <BrandLockup className="mb-6" />
        <h1 className="text-2xl font-semibold text-text-primary">{resolvedTitle}</h1>
        <p className="mt-2 text-sm text-text-secondary">{resolvedDescription}</p>

        {otpPhase.status === "conflict" ? (
          <div className="mt-6 space-y-3" data-testid="identity-gate-conflict">
            <p className="text-sm text-text-secondary">
              <span className="text-text-primary">{otpPhase.email}</span> already
              has an account. Keep this device or switch to that account.
            </p>
            <div className="flex flex-col gap-2 sm:flex-row">
              <Button data-testid="identity-gate-keep-local" onClick={handleKeepLocal}>
                Keep this session
              </Button>
              <Button
                variant="ghost"
                data-testid="identity-gate-switch"
                onClick={() => handleSwitchToExisting(otpPhase.existing)}
              >
                Switch to existing account
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
                    ? "Sending…"
                    : otpPhase.status === "code_sent"
                      ? "Resend code"
                      : "Send code"}
                </Button>
              ) : (
                <Button
                  data-testid="identity-gate-continue"
                  disabled={otpBusy}
                  onClick={() => void handleContinue()}
                >
                  {otpBusy ? "Checking…" : "Continue"}
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
                    placeholder="6-digit code"
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
                    {otpBusy ? "Verifying…" : "Verify"}
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
                  Use a different email
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
    </main>
  );
}
