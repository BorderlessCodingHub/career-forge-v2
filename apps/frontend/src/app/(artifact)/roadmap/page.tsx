"use client";

import { useTranslations } from "next-intl";
import { Suspense } from "react";

import { ProductEntryGate } from "@/components/auth";
import RoadmapArtifactPageContent from "./RoadmapArtifactContent";

export default function RoadmapArtifactPage() {
  const t = useTranslations("roadmap");

  return (
    <ProductEntryGate>
      <Suspense
        fallback={
          <p className="py-20 text-center text-sm text-text-muted animate-pulse">
            {t("loadingTrail")}
          </p>
        }
      >
        <RoadmapArtifactPageContent />
      </Suspense>
    </ProductEntryGate>
  );
}
