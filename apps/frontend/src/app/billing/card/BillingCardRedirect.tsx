"use client";

import { useEffect, useState } from "react";

import { startBillingPortal } from "@/lib/api-client";
import { redirectToCardUpdate } from "@/lib/billing-card";

export function BillingCardRedirect() {
  const [message, setMessage] = useState("Opening card update…");

  useEffect(() => {
    void redirectToCardUpdate(startBillingPortal, (url) => {
      window.location.assign(url);
    }).catch(() => {
      setMessage("Card update is unavailable right now.");
    });
  }, []);

  return (
    <main className="min-h-screen grid-dots flex items-center justify-center p-8">
      <p className="text-text-secondary">{message}</p>
    </main>
  );
}
