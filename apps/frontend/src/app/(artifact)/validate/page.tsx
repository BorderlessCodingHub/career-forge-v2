"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { ProductEntryGate } from "@/components/auth";
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
          Select a node on the trail to start validation.
        </p>
        <Link
          href="/roadmap"
          className="mt-4 inline-block text-sm font-medium text-accent hover:underline"
        >
          Back to trail →
        </Link>
      </div>
    );
  }

  return <InterviewLoop nodeId={nodeId} mode={mode} />;
}

export default function ValidatePage() {
  return (
    <ProductEntryGate>
      <Suspense
        fallback={
          <p className="py-20 text-center text-sm text-text-muted animate-pulse">
            Loading validation…
          </p>
        }
      >
        <ValidatePageContent />
      </Suspense>
    </ProductEntryGate>
  );
}
