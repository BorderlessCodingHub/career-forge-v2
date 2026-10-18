import { Suspense } from "react";

import { BillingReturnClient } from "./BillingReturnClient";

export default function BillingReturnPage() {
  return (
    <Suspense fallback={null}>
      <BillingReturnClient />
    </Suspense>
  );
}
