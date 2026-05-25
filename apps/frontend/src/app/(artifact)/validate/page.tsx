"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { ValidationInterview } from "@/components/validation";

function ValidatePageContent() {
  const searchParams = useSearchParams();
  const nodeId = searchParams.get("node") ?? "http";

  return <ValidationInterview nodeId={nodeId} />;
}

export default function ValidatePage() {
  return (
    <Suspense
      fallback={
        <p className="py-20 text-center text-sm text-text-muted animate-pulse">
          Carregando validação…
        </p>
      }
    >
      <ValidatePageContent />
    </Suspense>
  );
}
