"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { InterviewLoop, type InterviewMode } from "@/components/validation";

function parseMode(value: string | null): InterviewMode {
  return value === "quick" ? "quick" : "loop";
}

function ValidatePageContent() {
  const searchParams = useSearchParams();
  const nodeId = searchParams.get("node");
  const mode = parseMode(searchParams.get("mode"));

  if (!nodeId) {
    return (
      <div className="mx-auto max-w-lg py-20 text-center">
        <p className="text-sm text-text-secondary">
          Selecione um tópico na trilha para iniciar a validação.
        </p>
      </div>
    );
  }

  return <InterviewLoop nodeId={nodeId} mode={mode} />;
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
