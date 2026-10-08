import { ProductEntryGate } from "@/components/auth";

import { BillingCardRedirect } from "./BillingCardRedirect";

export default function BillingCardPage() {
  return (
    <ProductEntryGate>
      <BillingCardRedirect />
    </ProductEntryGate>
  );
}
