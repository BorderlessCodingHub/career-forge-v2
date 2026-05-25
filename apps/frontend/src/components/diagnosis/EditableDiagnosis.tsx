"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui";
import type { DiagnosisResponse } from "@/types/contracts";
import {
  getStoredDiagnosis,
  setStoredDiagnosis,
} from "@/lib/onboarding-session";

type EditableDiagnosisProps = {
  initialDiagnosis?: DiagnosisResponse | null;
};

function EditableList({
  title,
  items,
  tone,
  onChange,
}: {
  title: string;
  items: string[];
  tone: "strength" | "gap" | "priority";
  onChange: (items: string[]) => void;
}) {
  const toneClasses = {
    strength: "border-success/20 bg-success/5",
    gap: "border-warning/20 bg-warning/5",
    priority: "border-accent/20 bg-accent/5",
  }[tone];

  return (
    <div className={`rounded-card border p-5 ${toneClasses}`}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium uppercase tracking-wide text-text-secondary">
          {title}
        </h3>
        <span className="rounded-full bg-surface px-2 py-0.5 text-xs text-text-muted">
          {items.length}
        </span>
      </div>
      <div className="space-y-3">
        {items.map((item, index) => (
          <textarea
            key={`${title}-${index}`}
            data-testid={`${tone}-item-${index}`}
            className="min-h-[72px] w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text-primary outline-none ring-accent focus:ring-2"
            value={item}
            onChange={(event) => {
              const next = [...items];
              next[index] = event.target.value;
              onChange(next);
            }}
          />
        ))}
      </div>
    </div>
  );
}

export function EditableDiagnosis({ initialDiagnosis }: EditableDiagnosisProps) {
  const router = useRouter();
  const [diagnosis, setDiagnosis] = useState<DiagnosisResponse | null>(
    initialDiagnosis ?? null,
  );

  useEffect(() => {
    if (!diagnosis) {
      setDiagnosis(getStoredDiagnosis());
    }
  }, [diagnosis]);

  useEffect(() => {
    if (!diagnosis) {
      router.replace("/onboarding");
    }
  }, [diagnosis, router]);

  if (!diagnosis) {
    return (
      <main className="min-h-screen grid-dots p-8">
        <p className="text-text-secondary">Carregando diagnóstico…</p>
      </main>
    );
  }

  const updateDiagnosis = (patch: Partial<DiagnosisResponse>) => {
    setDiagnosis((current) => {
      if (!current) return current;
      const next = { ...current, ...patch };
      setStoredDiagnosis(next);
      return next;
    });
  };

  return (
    <main className="min-h-screen grid-dots px-4 py-10" data-testid="editable-diagnosis">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-sm text-text-secondary">
            <span className="h-2 w-2 rounded-full bg-accent-mint" />
            Perfil: <strong className="text-text-primary">{diagnosis.profile.label}</strong>
          </div>
          <h1 className="mt-4 text-4xl font-semibold text-text-primary">
            Seu diagnóstico
          </h1>
          <p className="mt-3 max-w-3xl text-text-secondary">
            Ajuste fortes, lacunas e prioridades antes de forjar sua trilha. Esta
            é a foto de hoje — ela recalibra a cada validação.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <EditableList
            title="Pontos fortes"
            tone="strength"
            items={diagnosis.strengths}
            onChange={(strengths) => updateDiagnosis({ strengths })}
          />
          <EditableList
            title="Lacunas"
            tone="gap"
            items={diagnosis.gaps}
            onChange={(gaps) => updateDiagnosis({ gaps })}
          />
          <EditableList
            title="Prioridades iniciais"
            tone="priority"
            items={diagnosis.starting_priorities}
            onChange={(starting_priorities) => updateDiagnosis({ starting_priorities })}
          />
        </div>

        <div className="mt-6 rounded-card border border-border bg-surface p-5 text-sm text-text-secondary">
          <strong className="text-text-primary">Avaliação por evidência.</strong>{" "}
          Career Forge não deixa marcar tópicos como concluídos sem provar
          entendimento numa entrevista com a IA.
        </div>

        <div className="mt-8 flex flex-wrap items-center gap-4">
          <Link href="/onboarding">
            <Button variant="ghost">Voltar ao diagnóstico</Button>
          </Link>
          <Link href="/forge" data-testid="generate-roadmap">
            <Button>Gerar roadmap →</Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
