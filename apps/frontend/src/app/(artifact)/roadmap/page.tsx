"use client";

import { Suspense } from "react";

import { ProductEntryGate } from "@/components/auth";
import RoadmapArtifactPageContent from "./RoadmapArtifactContent";

export default function RoadmapArtifactPage() {
  return (
    <ProductEntryGate>
      <Suspense
        fallback={
          <p className="py-20 text-center text-sm text-text-muted animate-pulse">
            Loading trail…
          </p>
        }
      >
        <RoadmapArtifactPageContent />
      </Suspense>
    </ProductEntryGate>
  );
}
