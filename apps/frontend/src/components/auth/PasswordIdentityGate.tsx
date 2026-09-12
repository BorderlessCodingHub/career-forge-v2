"use client";

import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";

import { IdentityGateShell } from "@/components/auth/IdentityGateShell";
import { Button } from "@/components/ui";
import { signInWithPassword } from "@/lib/api-client";

type PasswordIdentityGateProps = {
  forgotPasswordUrl?: string;
  signupUrl?: string;
  onVerified: () => void;
};

export function PasswordIdentityGate({
  forgotPasswordUrl = "",
  signupUrl = "",
  onVerified,
}: PasswordIdentityGateProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [signupOpen, setSignupOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const forgot = forgotPasswordUrl.trim();
  const signup = signupUrl.trim();

  async function handleSignIn() {
    const trimmedEmail = email.trim();
    if (!trimmedEmail || !password) {
      setError("Enter your email and password.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await signInWithPassword(trimmedEmail, password);
      onVerified();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid email or password");
    } finally {
      setBusy(false);
    }
  }

  return (
    <IdentityGateShell screen="identity-gate-password">
      <div className="mx-auto max-w-md rounded-md border border-border bg-surface px-6 py-8">
        <h1 className="text-2xl font-semibold text-text-primary">Sign in</h1>
        <p className="mt-2 text-sm text-text-secondary">
          Use your Borderless Platform email and password.
        </p>

        <form
          className="mt-6 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            void handleSignIn();
          }}
        >
          <label className="block space-y-1">
            <span className="text-sm text-text-secondary">Email</span>
            <input
              type="email"
              autoComplete="email"
              className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
              placeholder="you@example.com"
              value={email}
              disabled={busy}
              data-testid="identity-gate-email"
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label className="block space-y-1">
            <span className="text-sm text-text-secondary">Password</span>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                className="w-full rounded-md border border-border bg-bg px-3 py-2 pr-12 text-sm text-text-primary"
                value={password}
                disabled={busy}
                data-testid="identity-gate-password"
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-2 flex items-center text-text-muted"
                data-testid="identity-gate-toggle-password"
                aria-label={showPassword ? "Hide password" : "Show password"}
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
              Forgot password?
            </a>
          ) : null}

          <Button
            type="submit"
            className="w-full"
            disabled={busy}
            data-testid="identity-gate-signin"
          >
            {busy ? "Signing in…" : "Sign in"}
          </Button>
        </form>

        {signup ? (
          <p className="mt-4 text-sm text-text-secondary">
            Don&apos;t have an account?{" "}
            <button
              type="button"
              className="text-accent underline-offset-2 hover:underline"
              data-testid="identity-gate-signup"
              onClick={() => setSignupOpen(true)}
            >
              Sign up
            </button>
          </p>
        ) : null}

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
            <h2
              id="identity-gate-signup-title"
              className="text-lg font-semibold text-text-primary"
            >
              Create a Borderless account
            </h2>
            <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-text-secondary">
              <li>
                Career Forge uses your <strong>Borderless Platform</strong> account.
                You don&apos;t create a password here.
              </li>
              <li>Open Borderless, complete sign up, verify email if they ask.</li>
              <li>
                Return to <strong>this tab</strong> and sign in with the same email
                and password.
              </li>
            </ol>
            <div className="mt-6 flex flex-col gap-2">
              <a
                href={signup}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md bg-accent px-4 py-2 text-center text-sm font-medium text-white hover:opacity-90"
                data-testid="identity-gate-signup-open-borderless"
              >
                Create account on Borderless Platform
              </a>
              <Button
                type="button"
                variant="ghost"
                data-testid="identity-gate-signup-already"
                onClick={() => setSignupOpen(false)}
              >
                I already have an account
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </IdentityGateShell>
  );
}
