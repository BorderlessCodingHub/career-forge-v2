"use client";

import { Suspense } from "react";
import { useTranslations } from "next-intl";

import { ProductEntryGate } from "@/components/auth";

import ReferenceViewerContent from "./ReferenceViewerContent";

export default function ReferenceViewerPage() {
  const t = useTranslations("reference");
  return (
    <ProductEntryGate>
      <Suspense
        fallback={
          <p className="py-20 text-center text-sm text-text-muted animate-pulse">
            {t("loading")}
          </p>
        }
      >
        <ReferenceViewerContent />
      </Suspense>
    </ProductEntryGate>
  );
}
