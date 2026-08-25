"use client";

import { Suspense } from "react";

import { ProductEntryGate } from "@/components/auth";

import ReferenceViewerContent from "./ReferenceViewerContent";

export default function ReferenceViewerPage() {
  return (
    <ProductEntryGate>
      <Suspense
        fallback={
          <p className="py-20 text-center text-sm text-text-muted animate-pulse">
            Loading Reference…
          </p>
        }
      >
        <ReferenceViewerContent />
      </Suspense>
    </ProductEntryGate>
  );
}
