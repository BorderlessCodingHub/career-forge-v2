"use client";

import Link from "next/link";
import { BookOpenCheck } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui";
import type { PlanUpdateResponse, ValidationResponse } from "@/types/contracts";

import { ScoreRing } from "./ScoreRing";

type ValidationResultProps = {
  nodeTitle: string;
  result: ValidationResponse;
  planUpdate?: PlanUpdateResponse | null;
  onRetry: () => void;
};

export function ValidationResult({
  nodeTitle,
  result,
  planUpdate,
  onRetry,
}: ValidationResultProps) {
  const [accordionOpen, setAccordionOpen] = useState(false);
  const passed = result.status === "aprovado";

  return (
    <div className="mx-auto max-w-4xl px-4 py-10" data-screen="validation-result">
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4 rounded-md border border-border bg-surface px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-accent/20 text-accent">
            <BookOpenCheck className="h-5 w-5" />
          </div>
          <p className="font-medium text-text-primary">{nodeTitle}</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span>Resultado</span>
          <span className="h-2 w-2 rounded-full bg-success" />
          <span className="h-2 w-2 rounded-full bg-success" />
          <span className="h-2 w-2 rounded-full bg-success" />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
        <div className="flex flex-col items-center gap-4 rounded-md border border-border bg-surface-elevated p-6">
          <ScoreRing score={result.score} status={result.status} />
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-widest ${
              passed
                ? "bg-success/15 text-success"
                : "bg-warning/15 text-warning"
            }`}
          >
            {passed ? "Aprovado" : "Revisar"}
          </span>
          <p className="text-center text-sm text-text-secondary">
            {passed
              ? "Evidências suficientes — mastery validado."
              : "Você está perto, mas ainda não passou."}
          </p>
        </div>

        <div className="space-y-4">
          {result.strengths.length > 0 && (
            <div className="rounded-md border border-success/30 bg-success/5 p-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-success">
                Você acertou
              </p>
              <ul className="mt-3 space-y-2 text-sm text-text-secondary">
                {result.strengths.map((item) => (
                  <li key={item} className="flex gap-2">
                    <span className="text-success">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.gaps.length > 0 && (
            <div className="rounded-md border border-warning/30 bg-warning/5 p-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-warning">
                Precisa melhorar
              </p>
              <ul className="mt-3 space-y-2 text-sm text-text-secondary">
                {result.gaps.map((item) => (
                  <li key={item} className="flex gap-2">
                    <span className="text-warning">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="rounded-md border border-accent/30 bg-accent/10 p-4">
            <p className="text-xs font-semibold uppercase tracking-widest text-accent">
              Próximo passo
            </p>
            <p className="mt-2 text-sm text-text-secondary">{result.next_action}</p>
          </div>

          <div className="rounded-md border border-border bg-surface">
            <button
              type="button"
              className="flex w-full items-center justify-between px-4 py-3 text-left text-sm text-text-secondary"
              onClick={() => setAccordionOpen((open) => !open)}
            >
              <span>Resumo para o mentor (Borderless)</span>
              <span>{accordionOpen ? "▴" : "▾"}</span>
            </button>
            {accordionOpen && (
              <p className="border-t border-border px-4 py-3 text-sm text-text-muted">
                {result.mentor_summary}
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
        <Link href={passed ? "/roadmap" : "/roadmap?adaptive=1"}>
          <Button variant="ghost">← Voltar à trilha</Button>
        </Link>
        <div className="flex flex-wrap gap-2">
          {!passed && planUpdate && (
            <Link href="/roadmap?adaptive=1">
              <Button data-testid="view-adaptive-roadmap">
                Ver trilha adaptada →
              </Button>
            </Link>
          )}
          <Button variant="ghost" onClick={onRetry}>
            Refazer validação
          </Button>
        </div>
      </div>
    </div>
  );
}
