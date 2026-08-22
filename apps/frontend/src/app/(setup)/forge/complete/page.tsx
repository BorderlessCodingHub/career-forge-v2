"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { StreamReveal } from "@/components/forge";
import { Button } from "@/components/ui";
import {
  absoluteAppUrl,
  emailResumeLink,
  listForges,
  mintResumeLink,
  OtpEmailOwnedError,
  requestOtp,
  verifyOtp,
} from "@/lib/api-client";
import { getForgeGraph, type ForgeGraphNode } from "@/lib/forge-session";
import { adoptSession, getAccessToken } from "@/lib/user-session";
import type { OtpEmailOwnedConflict } from "@/types/contracts";

type OtpPhase =
  | { status: "idle" }
  | { status: "code_sent"; email: string }
  | { status: "verifying" }
  | { status: "verified" }
  | {
      status: "conflict";
      email: string;
      existing: OtpEmailOwnedConflict["existing"];
    };

function readJwtProvider(token: string | null): string | null {
  if (!token) return null;
  try {
    const part = token.split(".")[1];
    if (!part) return null;
    const json = atob(part.replace(/-/g, "+").replace(/_/g, "/"));
    const payload = JSON.parse(json) as { provider?: unknown };
    return typeof payload.provider === "string" ? payload.provider : null;
  } catch {
    return null;
  }
}

export default function ForgeCompletePage() {
  const router = useRouter();
  const [graph, setGraph] = useState<ForgeGraphNode[] | null>(null);
  const [revealed, setRevealed] = useState(0);
  const [resumeUrl, setResumeUrl] = useState<string | null>(null);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [emailSendBusy, setEmailSendBusy] = useState(false);
  const [emailSendError, setEmailSendError] = useState<string | null>(null);
  const [resumePublicId, setResumePublicId] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [otpPhase, setOtpPhase] = useState<OtpPhase>({ status: "idle" });
  const [otpBusy, setOtpBusy] = useState(false);
  const [otpError, setOtpError] = useState<string | null>(null);
  const resumeMintedRef = useRef(false);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const autoScrollRef = useRef(true);

  useEffect(() => {
    if (readJwtProvider(getAccessToken()) === "email") {
      setOtpPhase({ status: "verified" });
    }
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      const { scrollHeight, scrollTop, clientHeight } = document.documentElement;
      autoScrollRef.current = scrollHeight - scrollTop - clientHeight < 150;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
    setGraph(getForgeGraph());
  }, []);

  useEffect(() => {
    if (!graph?.length) return;
    if (revealed >= graph.length) return;
    const timer = setTimeout(() => setRevealed((n) => n + 1), 280);
    return () => clearTimeout(timer);
  }, [graph, revealed]);

  useEffect(() => {
    if (revealed === 0) return;
    if (!autoScrollRef.current) return;
    const { scrollHeight, clientHeight } = document.documentElement;
    if (scrollHeight <= clientHeight) return;
    requestAnimationFrame(() => {
      sentinelRef.current?.scrollIntoView({ behavior: "smooth" });
    });
  }, [revealed]);

  useEffect(() => {
    if (!graph?.length) return;
    if (resumeMintedRef.current) return;
    resumeMintedRef.current = true;
    let cancelled = false;
    (async () => {
      try {
        const { items } = await listForges();
        const target = items.find((item) => item.is_active) ?? items[0];
        if (!target) {
          if (!cancelled) {
            setResumeError("Resume link unavailable — no forge artifact yet.");
          }
          return;
        }
        const minted = await mintResumeLink(target.public_id);
        if (!cancelled) {
          setResumePublicId(target.public_id);
          setResumeUrl(absoluteAppUrl(minted.path));
        }
      } catch (err) {
        if (!cancelled) {
          setResumeError(
            err instanceof Error ? err.message : "Failed to mint resume link",
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [graph]);

  async function handleRequestCode() {
    const next = email.trim();
    if (!next) {
      setOtpError("Enter an email to verify.");
      return;
    }
    setOtpBusy(true);
    setOtpError(null);
    try {
      const res = await requestOtp(next);
      setEmail(res.email);
      setOtpPhase({ status: "code_sent", email: res.email });
      setCode("");
    } catch (err) {
      setOtpError(err instanceof Error ? err.message : "Failed to send code");
    } finally {
      setOtpBusy(false);
    }
  }

  async function handleVerifyCode() {
    const currentEmail =
      otpPhase.status === "code_sent" || otpPhase.status === "conflict"
        ? otpPhase.email
        : email.trim();
    const nextCode = code.trim();
    if (!currentEmail || !nextCode) {
      setOtpError("Enter the 6-digit code from your email.");
      return;
    }
    setOtpBusy(true);
    setOtpError(null);
    setOtpPhase({ status: "verifying" });
    try {
      const res = await verifyOtp(currentEmail, nextCode);
      adoptSession(res.access_token, res.external_id);
      setOtpPhase({ status: "verified" });
    } catch (err) {
      if (err instanceof OtpEmailOwnedError) {
        setOtpPhase({
          status: "conflict",
          email: currentEmail,
          existing: err.conflict.existing,
        });
        setOtpError(null);
      } else {
        setOtpPhase({ status: "code_sent", email: currentEmail });
        setOtpError(err instanceof Error ? err.message : "Verification failed");
      }
    } finally {
      setOtpBusy(false);
    }
  }

  function handleKeepLocal() {
    // Stay on this screen — try a different email to verify this anon session.
    setOtpPhase({ status: "idle" });
    setCode("");
    setOtpError("Kept this session. Verify a different email to continue.");
  }

  function handleSwitchToExisting(existing: OtpEmailOwnedConflict["existing"]) {
    adoptSession(existing.access_token, existing.external_id);
    setOtpPhase({ status: "verified" });
    router.push("/roadmap");
  }

  if (!graph?.length) {
    return (
      <main className="min-h-screen grid-dots p-8">
        <p className="text-text-secondary">No forged graph yet.</p>
        <Link href="/forge" className="mt-4 inline-block text-accent">
          Back to forge
        </Link>
      </main>
    );
  }

  const done = revealed >= graph.length;
  const verified = otpPhase.status === "verified";

  return (
    <main
      className="min-h-screen grid-dots px-4 py-10"
      data-screen="forge-reveal"
    >
      <div className="mx-auto max-w-2xl">
        <h1 className="text-3xl font-semibold text-text-primary">
          Your trail is ready
        </h1>
        <p className="mt-2 text-text-secondary">
          Each chapter of your plan appears below. Verify your email to unlock
          the trail.
        </p>

        <ol className="mt-10 space-y-4">
          {graph.slice(0, revealed).map((node) => (
            <li
              key={node.node_id}
              className="animate-[reveal_400ms_ease-out]"
              style={{ animationFillMode: "backwards" }}
            >
              <div className="rounded-md border border-border bg-surface px-4 py-3">
                <StreamReveal
                  text={`${node.title ?? node.node_id} · ${node.status} · ${node.mastery_score}%`}
                />
              </div>
            </li>
          ))}
        </ol>
        <div ref={sentinelRef} />

        {done && (
          <div className="mt-10 space-y-4">
            <div
              className="rounded-md border border-border bg-surface px-4 py-3"
              data-testid="forge-otp-gate"
            >
              <p className="text-sm font-medium text-text-primary">
                Verify your email to continue
              </p>
              <p className="mt-1 text-sm text-text-secondary">
                We send a 6-digit code (check backend logs in local dev). This
                unlocks your trail and keeps this forge tied to your account.
              </p>

              {otpPhase.status === "conflict" ? (
                <div className="mt-4 space-y-3" data-testid="forge-otp-conflict">
                  <p className="text-sm text-text-secondary">
                    <span className="text-text-primary">{otpPhase.email}</span>{" "}
                    already has an account. Keep forging on this device, or
                    switch to that account.
                  </p>
                  <div className="flex flex-col gap-2 sm:flex-row">
                    <Button
                      data-testid="forge-otp-keep-local"
                      onClick={handleKeepLocal}
                    >
                      Keep this session
                    </Button>
                    <Button
                      variant="ghost"
                      data-testid="forge-otp-switch"
                      onClick={() => handleSwitchToExisting(otpPhase.existing)}
                    >
                      Switch to existing account
                    </Button>
                  </div>
                </div>
              ) : verified ? (
                <p
                  className="mt-3 text-sm text-text-secondary"
                  data-testid="forge-otp-verified"
                >
                  Email verified. You can explore your trail.
                </p>
              ) : (
                <div className="mt-3 space-y-3">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                    <input
                      type="email"
                      className="min-w-0 flex-1 rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
                      placeholder="you@example.com"
                      value={email}
                      disabled={otpBusy || otpPhase.status === "code_sent"}
                      data-testid="forge-otp-email"
                      onChange={(e) => setEmail(e.target.value)}
                    />
                    <Button
                      variant="ghost"
                      data-testid="forge-otp-request"
                      disabled={otpBusy}
                      onClick={() => void handleRequestCode()}
                    >
                      {otpBusy && otpPhase.status === "idle"
                        ? "Sending…"
                        : otpPhase.status === "code_sent"
                          ? "Resend code"
                          : "Send code"}
                    </Button>
                  </div>
                  {(otpPhase.status === "code_sent" ||
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
                          data-testid="forge-otp-code"
                          onChange={(e) =>
                            setCode(
                              e.target.value.replace(/\D/g, "").slice(0, 6),
                            )
                          }
                        />
                        <Button
                          data-testid="forge-otp-verify"
                          disabled={otpBusy || code.trim().length !== 6}
                          onClick={() => void handleVerifyCode()}
                        >
                          {otpBusy ? "Verifying…" : "Verify"}
                        </Button>
                      </div>
                      <button
                        type="button"
                        className="text-sm text-accent underline-offset-2 hover:underline"
                        data-testid="forge-otp-change-email"
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
                <p
                  className="mt-2 text-sm text-red-400"
                  data-testid="forge-otp-error"
                >
                  {otpError}
                </p>
              ) : null}
            </div>

            {verified ? (
              <Link href="/roadmap">
                <Button data-testid="forge-to-roadmap">
                  Explore vertical trail →
                </Button>
              </Link>
            ) : (
              <Button data-testid="forge-to-roadmap" disabled>
                Verify email to continue
              </Button>
            )}

            <div
              className="rounded-md border border-border bg-surface px-4 py-3"
              data-testid="forge-resume-copy"
            >
              <p className="text-sm font-medium text-text-primary">
                Save a resume link
              </p>
              <p className="mt-1 text-sm text-text-secondary">
                Single-use · expires in ~7 days. Copy it now — you will not see
                this link again on this screen.
              </p>
              {resumeUrl ? (
                <div className="mt-3 space-y-2">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                    <code className="block flex-1 truncate rounded bg-bg px-2 py-1 text-xs text-text-secondary">
                      {resumeUrl}
                    </code>
                    <Button
                      variant="ghost"
                      data-testid="forge-resume-copy-btn"
                      onClick={() => {
                        void navigator.clipboard.writeText(resumeUrl).then(() => {
                          setCopied(true);
                        });
                      }}
                    >
                      {copied ? "Copied" : "Copy resume link"}
                    </Button>
                  </div>
                  {verified && resumePublicId ? (
                    <div className="space-y-1">
                      <Button
                        variant="ghost"
                        data-testid="forge-resume-email-btn"
                        disabled={emailSendBusy || emailSent}
                        onClick={() => {
                          void (async () => {
                            setEmailSendBusy(true);
                            setEmailSendError(null);
                            try {
                              const res = await emailResumeLink(resumePublicId);
                              setEmailSent(true);
                              setResumeUrl(absoluteAppUrl(res.path));
                            } catch (err) {
                              setEmailSendError(
                                err instanceof Error
                                  ? err.message
                                  : "Failed to email resume link",
                              );
                            } finally {
                              setEmailSendBusy(false);
                            }
                          })();
                        }}
                      >
                        {emailSent
                          ? "Sent to your email"
                          : emailSendBusy
                            ? "Sending…"
                            : "Email me this link"}
                      </Button>
                      {emailSendError ? (
                        <p
                          className="text-sm text-red-400"
                          data-testid="forge-resume-email-error"
                        >
                          {emailSendError}
                        </p>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              ) : (
                <p className="mt-2 text-sm text-text-secondary">
                  {resumeError ?? "Preparing resume link…"}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
