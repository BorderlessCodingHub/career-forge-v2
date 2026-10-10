"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

import { Button } from "@/components/ui";
import { startBillingCheckout } from "@/lib/api-client";

type PaywallPanelProps = {
  checkoutAvailable: boolean;
};

/** Shown when an external account has spent its included forge and has no subscription. */
export function PaywallPanel({ checkoutAvailable }: PaywallPanelProps) {
  const t = useTranslations("paywall");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubscribe() {
    setBusy(true);
    setError(null);
    try {
      const url = await startBillingCheckout();
      window.location.assign(url);
    } catch (err) {
      setBusy(false);
      setError(err instanceof Error ? err.message : t("checkoutFailed"));
    }
  }

  return (
    <div
      className="rounded-md border border-accent/30 bg-surface px-4 py-4"
      data-testid="paywall-panel"
      role="status"
    >
      <p className="text-xs font-semibold uppercase tracking-widest text-accent">
        {t("eyebrow")}
      </p>
      <p className="mt-2 text-sm text-text-primary">{t("body")}</p>
      <p className="mt-2 text-sm text-text-secondary">{t("audience")}</p>
      {checkoutAvailable ? (
        <Button
          className="mt-4"
          data-testid="paywall-subscribe"
          disabled={busy}
          onClick={() => void handleSubscribe()}
        >
          {busy ? t("opening") : t("subscribe")}
        </Button>
      ) : (
        <p className="mt-3 text-sm text-text-secondary" data-testid="paywall-allowlist">
          {t("allowlist")}
        </p>
      )}
      {error ? (
        <p className="mt-3 text-sm text-danger" data-testid="paywall-error">
          {error}
        </p>
      ) : null}
    </div>
  );
}
