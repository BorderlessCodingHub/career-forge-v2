"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useTranslations } from "next-intl";

import { IdentityGateShell } from "@/components/auth/IdentityGateShell";
import { Button } from "@/components/ui";
import { isExpiredAccountLink } from "@/lib/account-link";
import { resetCareerForgePassword } from "@/lib/api-client";

const PASSWORD_MIN_LENGTH = 8;

export default function ResetCareerForgePasswordPage() {
  const t = useTranslations("identity");
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expired, setExpired] = useState(false);

  async function handleSubmit() {
    const token = new URLSearchParams(window.location.search).get("token") ?? "";
    if (!token) {
      setExpired(true);
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
    setError(null);
    try {
      await resetCareerForgePassword(token, password);
      router.push("/");
    } catch (err) {
      if (isExpiredAccountLink(err)) setExpired(true);
      else setError(t("couldNotSavePassword"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <IdentityGateShell screen="account-reset">
      <div className="mx-auto max-w-md rounded-md border border-border bg-surface px-6 py-8">
        <h1 className="text-2xl font-semibold text-text-primary">{t("chooseNewPassword")}</h1>
        {expired ? (
          <>
            <p className="mt-4 text-sm text-text-primary" data-testid="account-link-expired">
              {t("linkExpired")}
            </p>
            <Link
              href="/?account=forgot"
              className="mt-4 inline-block text-sm text-accent underline-offset-2 hover:underline"
              data-testid="account-link-again"
            >
              {t("requestAnotherLink")}
            </Link>
          </>
        ) : (
          <form
            className="mt-6 space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              void handleSubmit();
            }}
          >
            <label className="block space-y-1">
              <span className="text-sm text-text-secondary">{t("password")}</span>
              <input
                type="password"
                autoComplete="new-password"
                className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
                value={password}
                disabled={busy}
                data-testid="account-reset-password"
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            <label className="block space-y-1">
              <span className="text-sm text-text-secondary">{t("confirmPassword")}</span>
              <input
                type="password"
                autoComplete="new-password"
                className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-primary"
                value={confirmPassword}
                disabled={busy}
                data-testid="account-reset-confirm"
                onChange={(event) => setConfirmPassword(event.target.value)}
              />
            </label>
            <Button type="submit" className="w-full" disabled={busy} data-testid="account-reset-submit">
              {t("chooseNewPassword")}
            </Button>
            {error ? (
              <p className="text-sm text-red-400" data-testid="account-reset-error">
                {error}
              </p>
            ) : null}
          </form>
        )}
      </div>
    </IdentityGateShell>
  );
}
