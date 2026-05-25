"use client";

import Link from "next/link";
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
