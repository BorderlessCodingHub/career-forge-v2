"use client";

import { Eye, EyeOff } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { IdentityGateShell } from "@/components/auth/IdentityGateShell";
import { Button } from "@/components/ui";
import {
  AccountExistsError,
  EmailUnconfirmedError,
  MailDeliveryError,
  registerCareerForgeAccount,
  requestCareerForgePasswordReset,
  resendCareerForgeConfirmation,
  signInWithCareerForgePassword,
  signInWithPassword,
} from "@/lib/api-client";

type PasswordIdentityGateProps = {
  forgotPasswordUrl?: string;
  signupUrl?: string;
  onVerified: () => void;
};

type CareerView = "signin" | "signup" | "forgot" | "check";

const PASSWORD_MIN_LENGTH = 8;

export function PasswordIdentityGate({
  forgotPasswordUrl = "",
  signupUrl = "",
  onVerified,
}: PasswordIdentityGateProps) {
  const t = useTranslations("identity");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [signupOpen, setSignupOpen] = useState(false);
  const [door, setDoor] = useState<"borderless" | "career_forge">("borderless");
  const [view, setView] = useState<CareerView>("signin");
  const [sentTo, setSentTo] = useState("");
  const [canResend, setCanResend] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const forgot = forgotPasswordUrl.trim();
  const signup = signupUrl.trim();

  useEffect(() => {
    const account = new URLSearchParams(window.location.search).get("account");
    if (account === "signup") {
      setDoor("career_forge");
      setView("signup");
    } else if (account === "forgot") {
      setDoor("career_forge");
      setView("forgot");
    }
  }, []);

  function resetFeedback() {
    setError(null);
    setNotice(null);
    setCanResend(false);
  }

  function accountErrorMessage(err: unknown, fallback: string): string {
    if (err instanceof MailDeliveryError) return t("couldNotSendEmail");
    if (err instanceof Error && err.message) return err.message;
    return fallback;
  }

  async function handleSignIn() {
    const trimmedEmail = email.trim();
    if (!trimmedEmail || !password) {
      setError(t("enterEmailPassword"));
      return;
    }
    setBusy(true);
    resetFeedback();
    try {
      await signInWithPassword(trimmedEmail, password);
      onVerified();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("invalidPassword"));
    } finally {
      setBusy(false);
    }
  }

  async function handleCareerForgeSignIn() {
    const trimmedEmail = email.trim();
    if (!trimmedEmail || !password) {
      setError(t("enterEmailPassword"));
      return;
    }
    setBusy(true);
    resetFeedback();
    try {
      await signInWithCareerForgePassword(trimmedEmail, password);
      onVerified();
    } catch (err) {
      if (err instanceof EmailUnconfirmedError) {
        setSentTo(trimmedEmail);
        setCanResend(true);
        setError(t("emailNotConfirmed"));
      } else {
        setError(err instanceof Error ? err.message : t("invalidPassword"));
      }
    } finally {
      setBusy(false);
    }
  }

  async function handleSignup() {
    const trimmedEmail = email.trim();
    const trimmedName = name.trim();
    if (!trimmedName) {
      setError(t("enterName"));
      return;
    }
    if (!trimmedEmail) {
      setError(t("enterEmailFirst"));
      return;
    }
    if (password.length < PASSWORD_MIN_LENGTH) {
      setError(t("passwordTooShort"));
      return;
    }
    if (password !== confirmPassword) {
      setError(t("passwordMismatch"));
      return;
    }
    setBusy(true);
    resetFeedback();
    try {
      const ack = await registerCareerForgeAccount(trimmedName, trimmedEmail, password);
      setSentTo(ack.email);
      setView("check");
    } catch (err) {
      if (err instanceof AccountExistsError) {
        setView("signin");
        setError(t("accountExists"));
      } else if (err instanceof MailDeliveryError) {
        setSentTo(trimmedEmail);
        setView("check");
        setError(t("couldNotSendEmail"));
      } else {
        setError(accountErrorMessage(err, t("couldNotSendEmail")));
      }
    } finally {
      setBusy(false);
    }
  }

  async function handleResend() {
    const target = (sentTo || email).trim();
    if (!target) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const ack = await resendCareerForgeConfirmation(target);
      setSentTo(ack.email);
      setCanResend(false);
      setNotice(t("confirmationSent", { email: ack.email }));
    } catch (err) {
      setError(accountErrorMessage(err, t("couldNotSendEmail")));
    } finally {
      setBusy(false);
    }
  }

  async function handleForgot() {
    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setError(t("enterEmailFirst"));
      return;
    }
    setBusy(true);
    resetFeedback();
    try {
      await requestCareerForgePasswordReset(trimmedEmail);
      setNotice(t("resetLinkSent"));
    } catch (err) {
      setError(accountErrorMessage(err, t("couldNotSendEmail")));
    } finally {
      setBusy(false);
    }
  }

  function backToBorderless() {
    setDoor("borderless");
    setView("signin");
    resetFeedback();
  }

  if (door === "career_forge") {
    return (
      <IdentityGateShell screen="identity-gate-password">
        <div className="mx-auto max-w-md rounded-md border border-border bg-surface px-6 py-8">
          <h1 className="text-2xl font-semibold text-text-primary">{t("careerForgeTitle")}</h1>
          <p className="mt-2 text-sm text-text-secondary">{t("careerForgeDescription")}</p>

          {view === "check" ? (
            <div className="mt-6 space-y-4">
              {error ? null : (
                <p className="text-sm text-text-primary" data-testid="identity-gate-career-forge-sent">
                  {t("confirmationSent", { email: sentTo })}
                </p>
              )}
              <Button
                type="button"
                className="w-full"
                disabled={busy}
                data-testid="identity-gate-career-forge-resend"
                onClick={() => void handleResend()}
              >
                {t("resendConfirmation")}
              </Button>
            </div>
          ) : null}

          {view === "signup" ? (
            <form
              className="mt-6 space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                void handleSignup();
              }}
            >
              <label className="block space-y-1">
                <span className="text-sm text-text-secondary">{t("fullName")}</span>
                <input
                  type="text"
                  autoComplete="name"
                  className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
                  value={name}
                  disabled={busy}
                  data-testid="identity-gate-career-forge-name"
                  onChange={(event) => setName(event.target.value)}
                />
              </label>
              <EmailField email={email} busy={busy} onChange={setEmail} label={t("email")} />
              <SecretField
                label={t("password")}
                value={password}
                shown={showPassword}
                autoComplete="new-password"
                testId="identity-gate-career-forge-password"
                toggleTestId="identity-gate-career-forge-toggle-password"
                showLabel={t("showPassword")}
                hideLabel={t("hidePassword")}
                disabled={busy}
                onChange={setPassword}
                onToggle={() => setShowPassword((open) => !open)}
              />
              <SecretField
                label={t("confirmPassword")}
                value={confirmPassword}
                shown={showConfirm}
                autoComplete="new-password"
                testId="identity-gate-career-forge-confirm"
                toggleTestId="identity-gate-career-forge-toggle-confirm"
                showLabel={t("showPassword")}
                hideLabel={t("hidePassword")}
                disabled={busy}
                onChange={setConfirmPassword}
                onToggle={() => setShowConfirm((open) => !open)}
              />
              <Button
                type="submit"
                className="w-full"
                disabled={busy}
                data-testid="identity-gate-career-forge-signup"
              >
                {t("signUp")}
              </Button>
            </form>
          ) : null}

          {view === "forgot" ? (
            <form
              className="mt-6 space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                void handleForgot();
              }}
            >
              <EmailField email={email} busy={busy} onChange={setEmail} label={t("email")} />
              <Button
                type="submit"
                className="w-full"
                disabled={busy}
                data-testid="identity-gate-career-forge-forgot-submit"
              >
                {t("sendResetLink")}
              </Button>
              {notice ? (
                <p className="text-sm text-text-primary" data-testid="identity-gate-career-forge-notice">
                  {notice}
                </p>
              ) : null}
            </form>
          ) : null}

          {view === "signin" ? (
            <form
              className="mt-6 space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                void handleCareerForgeSignIn();
              }}
            >
              <EmailField email={email} busy={busy} onChange={setEmail} label={t("email")} />
              <SecretField
                label={t("password")}
                value={password}
                shown={showPassword}
                autoComplete="current-password"
                testId="identity-gate-career-forge-password"
                toggleTestId="identity-gate-career-forge-toggle-password"
                showLabel={t("showPassword")}
                hideLabel={t("hidePassword")}
                disabled={busy}
                onChange={setPassword}
                onToggle={() => setShowPassword((open) => !open)}
              />
              <button
                type="button"
                className="text-sm text-accent underline-offset-2 hover:underline"
                data-testid="identity-gate-career-forge-forgot"
                onClick={() => {
                  setView("forgot");
                  resetFeedback();
                }}
              >
                {t("forgotCareerForgePassword")}
              </button>
              <Button
                type="submit"
                className="w-full"
                disabled={busy}
                data-testid="identity-gate-career-forge-signin"
              >
                {t("signIn")}
              </Button>
            </form>
          ) : null}

          {view === "signin" ? (
            <button
              type="button"
              className="mt-4 text-sm text-accent underline-offset-2 hover:underline"
              data-testid="identity-gate-career-forge-create"
              onClick={() => {
                setView("signup");
                resetFeedback();
              }}
            >
              {t("createCareerForgeAccount")}
            </button>
          ) : (
            <button
              type="button"
              className="mt-4 text-sm text-accent underline-offset-2 hover:underline"
              data-testid="identity-gate-career-forge-back-signin"
              onClick={() => {
                setView("signin");
                resetFeedback();
              }}
            >
              {t("backToCareerForgeSignIn")}
            </button>
          )}

          {canResend ? (
            <button
              type="button"
              className="mt-3 block text-sm text-accent underline-offset-2 hover:underline"
              data-testid="identity-gate-career-forge-resend"
              disabled={busy}
              onClick={() => void handleResend()}
            >
              {t("resendConfirmation")}
            </button>
          ) : null}

          <button
            type="button"
            className="mt-3 block text-sm text-text-secondary underline-offset-2 hover:underline"
            data-testid="identity-gate-back-borderless"
            onClick={backToBorderless}
          >
            {t("backToBorderless")}
          </button>
          {notice && view !== "forgot" ? (
            <p className="mt-3 text-sm text-text-primary" data-testid="identity-gate-career-forge-notice">
              {notice}
            </p>
          ) : null}
          {error ? (
            <p className="mt-3 text-sm text-red-400" data-testid="identity-gate-error">
              {error}
            </p>
          ) : null}
        </div>
      </IdentityGateShell>
    );
  }

  return (
    <IdentityGateShell screen="identity-gate-password">
      <div className="mx-auto max-w-md rounded-md border border-border bg-surface px-6 py-8">
        <h1 className="text-2xl font-semibold text-text-primary">{t("signIn")}</h1>
        <p className="mt-2 text-sm text-text-secondary">{t("passwordDescription")}</p>

        <form
          className="mt-6 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            void handleSignIn();
          }}
        >
          <EmailField
            email={email}
            busy={busy}
            onChange={setEmail}
            label={t("email")}
            testId="identity-gate-email"
          />

          <label className="block space-y-1">
            <span className="text-sm text-text-secondary">{t("password")}</span>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                className="w-full rounded-md border border-border bg-bg px-3 py-2 pr-12 text-sm text-text-primary"
                value={password}
                disabled={busy}
                data-testid="identity-gate-password"
                onChange={(event) => setPassword(event.target.value)}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-2 flex items-center text-text-muted"
                data-testid="identity-gate-toggle-password"
                aria-label={showPassword ? t("hidePassword") : t("showPassword")}
                onClick={() => setShowPassword((open) => !open)}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </label>

          {forgot ? (
            <a
              href={forgot}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block text-sm text-accent underline-offset-2 hover:underline"
              data-testid="identity-gate-forgot"
            >
              {t("forgotPassword")}
            </a>
          ) : null}

          <Button type="submit" className="w-full" disabled={busy} data-testid="identity-gate-signin">
            {busy ? t("signingIn") : t("signIn")}
          </Button>
        </form>

        {signup ? (
          <p className="mt-4 text-sm text-text-secondary">
            {t("noAccount")}{" "}
            <button
              type="button"
              className="text-accent underline-offset-2 hover:underline"
              data-testid="identity-gate-signup"
              onClick={() => setSignupOpen(true)}
            >
              {t("signUp")}
            </button>
          </p>
        ) : null}

        <button
          type="button"
          className="mt-4 text-sm text-accent underline-offset-2 hover:underline"
          data-testid="identity-gate-career-forge"
          onClick={() => {
            setDoor("career_forge");
            setView("signin");
            resetFeedback();
          }}
        >
          {t("useCareerForgePassword")}
        </button>

        {error ? (
          <p className="mt-3 text-sm text-red-400" data-testid="identity-gate-error">
            {error}
          </p>
        ) : null}
      </div>

      {signupOpen && signup ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
          data-testid="identity-gate-signup-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="identity-gate-signup-title"
        >
          <div className="w-full max-w-md rounded-md border border-border bg-surface px-6 py-6">
            <h2 id="identity-gate-signup-title" className="text-lg font-semibold text-text-primary">
              {t("createAccountTitle")}
            </h2>
            <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-text-secondary">
              <li>{t("signupStep1")}</li>
              <li>{t("signupStep2")}</li>
              <li>{t("signupStep3")}</li>
            </ol>
            <div className="mt-6 flex flex-col gap-2">
              <a
                href={signup}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md bg-accent px-4 py-2 text-center text-sm font-medium text-white hover:opacity-90"
                data-testid="identity-gate-signup-open-borderless"
              >
                {t("createOnBorderless")}
              </a>
              <Button
                type="button"
                variant="ghost"
                data-testid="identity-gate-signup-already"
                onClick={() => setSignupOpen(false)}
              >
                {t("alreadyHaveAccount")}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </IdentityGateShell>
  );
}

function EmailField({
  email,
  busy,
  onChange,
  label,
  testId = "identity-gate-career-forge-email",
}: {
  email: string;
  busy: boolean;
  onChange: (value: string) => void;
  label: string;
  testId?: string;
}) {
  return (
    <label className="block space-y-1">
      <span className="text-sm text-text-secondary">{label}</span>
      <input
        type="email"
        autoComplete="email"
        className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
        placeholder="you@example.com"
        value={email}
        disabled={busy}
        data-testid={testId}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function SecretField({
  label,
  value,
  shown,
  autoComplete,
  testId,
  toggleTestId,
  showLabel,
  hideLabel,
  disabled,
  onChange,
  onToggle,
}: {
  label: string;
  value: string;
  shown: boolean;
  autoComplete: string;
  testId: string;
  toggleTestId: string;
  showLabel: string;
  hideLabel: string;
  disabled: boolean;
  onChange: (value: string) => void;
  onToggle: () => void;
}) {
  return (
    <label className="block space-y-1">
      <span className="text-sm text-text-secondary">{label}</span>
      <div className="relative">
        <input
          type={shown ? "text" : "password"}
          autoComplete={autoComplete}
          className="w-full rounded-md border border-border bg-bg px-3 py-2 pr-12 text-sm text-text-primary"
          value={value}
          disabled={disabled}
          data-testid={testId}
          onChange={(event) => onChange(event.target.value)}
        />
        <button
          type="button"
          className="absolute inset-y-0 right-2 flex items-center text-text-muted"
          data-testid={toggleTestId}
          aria-label={shown ? hideLabel : showLabel}
          onClick={onToggle}
        >
          {shown ? <EyeOff size={16} /> : <Eye size={16} />}
        </button>
      </div>
    </label>
  );
}
