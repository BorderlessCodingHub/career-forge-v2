"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useEffect, useState } from "react";

import { syncBillingSession } from "@/lib/api-client";

type CheckoutReturnProps = {
  billing: string | null;
  sessionId: string | null;
};

type SyncState = "pending" | "paid" | "failed";

export function CheckoutReturn({ billing, sessionId }: CheckoutReturnProps) {
  const t = useTranslations("billing");
  const cancelled = billing === "cancel";
  const [syncState, setSyncState] = useState<SyncState>("pending");

  useEffect(() => {
    if (cancelled || billing !== "success" || !sessionId) {
      if (!cancelled) setSyncState("failed");
      return;
    }
    let cancelledEffect = false;
    syncBillingSession(sessionId)
      .then(() => {
        if (!cancelledEffect) setSyncState("paid");
      })
      .catch(() => {
        if (!cancelledEffect) setSyncState("failed");
      });
    return () => {
      cancelledEffect = true;
    };
  }, [billing, cancelled, sessionId]);

  const showForgesLink = cancelled || syncState === "paid";
  const message = cancelled
    ? t("nothingCharged")
    : syncState === "paid"
      ? t("thanks")
      : syncState === "failed"
        ? t("confirmFailed")
        : null;

  return (
    <main className="min-h-screen grid-dots flex items-center justify-center p-8">
      <div className="max-w-md text-center">
        {message ? <p className="text-text-primary">{message}</p> : null}
        {showForgesLink ? (
          <Link
            href="/forges"
            className="mt-6 inline-block rounded-md bg-accent px-4 py-2 text-sm font-medium text-white"
          >
            {t("seeForges")}
          </Link>
        ) : null}
      </div>
    </main>
  );
}
