"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { MockInterviewLoop, ValidationInterview } from "@/components/validation";

function ValidatePageContent() {
  const searchParams = useSearchParams();
  const nodeId = searchParams.get("node");
  const mode = searchParams.get("mode") ?? "loop";

  if (!nodeId) {
    return (
      <div className="mx-auto max-w-lg px-4 py-20 text-center">
        <p className="text-sm text-text-secondary">
          Selecione um nó na trilha para iniciar a validação.
        </p>
        <Link
          href="/roadmap"
          className="mt-4 inline-block text-sm font-medium text-accent hover:underline"
        >
          Voltar à trilha →
        </Link>
      </div>
    );
  }

  if (mode === "quick") {
    return <ValidationInterview nodeId={nodeId} />;
  }

  return <MockInterviewLoop nodeId={nodeId} />;
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
