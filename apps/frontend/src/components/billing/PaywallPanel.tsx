"use client";

import { useState } from "react";

import { Button } from "@/components/ui";
import { startBillingCheckout } from "@/lib/api-client";
import { PAYWALL_COPY } from "@/lib/paywall";

type PaywallPanelProps = {
  checkoutAvailable: boolean;
};

/** Clear paywall after the free forge — BASE/PSP never see this (CAR-46). */
export function PaywallPanel({ checkoutAvailable }: PaywallPanelProps) {
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
      setError(err instanceof Error ? err.message : "Checkout failed");
    }
  }

  return (
    <div
      className="rounded-md border border-accent/30 bg-surface px-4 py-4"
      data-testid="paywall-panel"
      role="status"
    >
      <p className="text-xs font-semibold uppercase tracking-widest text-accent">
        Free forge used
      </p>
      <p className="mt-2 text-sm text-text-primary">{PAYWALL_COPY}</p>
      <p className="mt-2 text-sm text-text-secondary">
        BASE and PSP members keep forging without Stripe. External learners
        subscribe to continue.
      </p>
      {checkoutAvailable ? (
        <Button
          className="mt-4"
          data-testid="paywall-subscribe"
          disabled={busy}
          onClick={() => void handleSubscribe()}
        >
          {busy ? "Opening checkout…" : "Subscribe"}
        </Button>
      ) : (
        <p className="mt-3 text-sm text-text-secondary" data-testid="paywall-allowlist">
          Checkout is not live yet. Ask to be added to the pilot billing
          allowlist.
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
