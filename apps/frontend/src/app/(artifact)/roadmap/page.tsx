"use client";

import { Suspense } from "react";

import RoadmapArtifactPageContent from "./RoadmapArtifactContent";

export default function RoadmapArtifactPage() {
  return (
    <Suspense
      fallback={
        <p className="py-20 text-center text-sm text-text-muted animate-pulse">
          Carregando trilha…
        </p>
      }
    >
      <RoadmapArtifactPageContent />
    </Suspense>
  );
}
