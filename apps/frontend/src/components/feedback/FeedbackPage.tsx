"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState, type FormEvent } from "react";

import {
  FeedbackLimitError,
  getMyProfile,
  submitLearnerFeedback,
} from "@/lib/api-client";
import { hasEmailIdentity } from "@/lib/user-session";

type Phase = "loading" | "signed-out" | "no-email" | "unavailable" | "ready";

function notePath(): string | null {
  if (typeof window === "undefined") return null;
  const from = new URLSearchParams(window.location.search).get("from");
  if (from && from.startsWith("/") && !from.includes("://")) return from;
  return window.location.pathname || null;
}

export function FeedbackPage() {
  const t = useTranslations("feedback");
  const [phase, setPhase] = useState<Phase>("loading");
  const [email, setEmail] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [thanks, setThanks] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (!hasEmailIdentity()) {
      setPhase("signed-out");
      return;
    }
    let cancelled = false;
    void getMyProfile()
      .then((profile) => {
        if (cancelled) return;
        if (!profile.email) {
          setPhase("no-email");
          return;
        }
        setEmail(profile.email);
        setPhase("ready");
      })
      .catch(() => {
        if (!cancelled) setPhase("unavailable");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim()) {
      setThanks(false);
      setError(t("required"));
      return;
    }
    setSending(true);
    setError(null);
    try {
      await submitLearnerFeedback({ message, path: notePath() });
      setMessage("");
      setThanks(true);
    } catch (cause) {
      setThanks(false);
      setError(cause instanceof FeedbackLimitError ? t("limit") : t("failed"));
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-xl px-6 py-10">
      <h1 className="text-2xl font-semibold text-text-primary">{t("title")}</h1>
      <p className="mt-3 text-sm leading-6 text-text-secondary" data-testid="feedback-courtesy">
        {t("courtesy")}
      </p>

      {phase === "signed-out" ? (
        <p className="mt-6 text-sm text-text-secondary" data-testid="feedback-blocked">
          {t("signedOut")}
        </p>
      ) : null}
      {phase === "no-email" ? (
        <p className="mt-6 text-sm text-text-secondary" data-testid="feedback-blocked">
          {t("noEmail")}
        </p>
      ) : null}
      {phase === "unavailable" ? (
        <p className="mt-6 text-sm text-text-secondary" data-testid="feedback-blocked">
          {t("unavailable")}
        </p>
      ) : null}

      {phase === "ready" && email ? (
        <form className="mt-6" onSubmit={(event) => void submit(event)}>
          <p className="text-xs uppercase tracking-widest text-text-muted">{t("emailLabel")}</p>
          <p className="mt-1 text-sm text-text-primary" data-testid="feedback-email">
            {email}
          </p>
          <label className="mt-5 block text-xs uppercase tracking-widest text-text-muted" htmlFor="feedback-message">
            {t("messageLabel")}
          </label>
          <textarea
            id="feedback-message"
            value={message}
            maxLength={2000}
            rows={6}
            disabled={sending}
            data-testid="feedback-message"
            className="mt-1 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-mint"
            onChange={(event) => setMessage(event.target.value)}
          />
          {thanks ? (
            <p className="mt-3 text-sm text-text-primary" data-testid="feedback-thanks">
              {t("thanks")}
            </p>
          ) : null}
          {error ? (
            <p className="mt-3 text-sm text-warning" role="alert" data-testid="feedback-error">
              {error}
            </p>
          ) : null}
          <button
            type="submit"
            disabled={sending}
            data-testid="feedback-submit"
            className="mt-4 inline-flex h-9 items-center rounded-md bg-accent px-4 text-xs font-medium text-white disabled:opacity-50"
          >
            {sending ? t("sending") : t("submit")}
          </button>
        </form>
      ) : null}
    </main>
  );
}
