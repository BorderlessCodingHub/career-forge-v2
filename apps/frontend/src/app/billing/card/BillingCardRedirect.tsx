"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { startBillingPortal } from "@/lib/api-client";
import { redirectToCardUpdate } from "@/lib/billing-card";

export function BillingCardRedirect() {
  const t = useTranslations("billing");
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    void redirectToCardUpdate(startBillingPortal, (url) => {
      window.location.assign(url);
    }).catch(() => {
      setFailed(true);
    });
  }, []);

  return (
    <main className="min-h-screen grid-dots flex items-center justify-center p-8">
      <p className="text-text-secondary">{failed ? t("unavailable") : t("opening")}</p>
    </main>
  );
}
