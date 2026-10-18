"use client";

import { useSearchParams } from "next/navigation";

import { ProductEntryGate } from "@/components/auth";
import { CheckoutReturn } from "@/components/billing/CheckoutReturn";

export function BillingReturnClient() {
  const params = useSearchParams();
  return (
    <ProductEntryGate>
      <CheckoutReturn
        billing={params.get("billing")}
        sessionId={params.get("session_id")}
      />
    </ProductEntryGate>
  );
}
