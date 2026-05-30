"use client";

import Link from "next/link";

import { Button } from "@/components/ui";
import type { MentorReportResponse, MentorReportValidationEntry } from "@/types/contracts";

import {
  formatLegacyMentorSummary,
  formatNodeTitleForDisplay,
  hasStructuredEvidence,
} from "./format-node-title";

type MentorReportViewProps = {
  report: MentorReportResponse;
};

function EvidenceBulletList({
  items,
  tone,
}: {
  items: string[];
  tone: "success" | "warning";
}) {
  const toneClass = tone === "success" ? "text-success" : "text-warning";

  return (
    <ul className="mt-2 space-y-2 text-sm text-text-secondary">
      {items.map((item) => (
        <li key={item} className="flex gap-2">
          <span className={toneClass}>•</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function MentorSummaryBlock({ entry }: { entry: MentorReportValidationEntry }) {
  const structured = hasStructuredEvidence(entry);

  if (structured) {
    return (
      <div className="mt-5 rounded-md border border-border bg-surface p-4">
        <p className="text-xs font-semibold uppercase tracking-widest text-text-muted">
          Resumo para mentor
        </p>

        {entry.gaps.length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-widest text-warning">
              Lacunas principais
            </p>
            <EvidenceBulletList items={entry.gaps} tone="warning" />
          </div>
        )}

        {entry.strengths.length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-widest text-success">
              Evidências positivas
            </p>
            <EvidenceBulletList items={entry.strengths} tone="success" />
          </div>
        )}

        {entry.recommended_intervention.trim() && (
          <div className="mt-4 rounded-md border border-accent/30 bg-accent/10 p-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-accent">
              Próximo passo
            </p>
            <p className="mt-2 text-sm text-text-secondary">
              {entry.recommended_intervention}
            </p>
          </div>
        )}
      </div>
    );
  }

  if (!entry.mentor_summary.trim()) return null;

  const legacyLines = formatLegacyMentorSummary(entry.mentor_summary);
  return (
    <div className="mt-5 rounded-md border border-border bg-surface p-4">
      <p className="text-xs font-semibold uppercase tracking-widest text-text-muted">
        Resumo para mentor
      </p>
      <div className="mt-2 space-y-2 text-sm text-text-secondary">
        {legacyLines.map((line) => (
          <p key={line}>{line}</p>
        ))}
      </div>
    </div>
  );
}

function ValidationCard({ entry }: { entry: MentorReportValidationEntry }) {
  const passed = entry.status === "aprovado";
  const displayTitle = formatNodeTitleForDisplay(entry.node_title, entry.node_id);

  return (
    <article
      className="rounded-md border border-border bg-surface-elevated p-5"
      data-testid={`mentor-report-entry-${entry.node_id}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-widest text-text-muted">Tópico avaliado</p>
          <h3 className="text-lg font-semibold text-text-primary">{displayTitle}</h3>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-text-primary">{entry.score}/100</p>
          <span
            className={`mt-1 inline-block rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-widest ${
              passed ? "bg-success/15 text-success" : "bg-warning/15 text-warning"
            }`}
          >
            {passed ? "Aprovado" : "Precisa revisar"}
          </span>
        </div>
      </div>

      <MentorSummaryBlock entry={entry} />
    </article>
  );
}

export function MentorReportView({ report }: MentorReportViewProps) {
  return (
    <div className="mx-auto max-w-4xl px-4 py-10" data-screen="mentor-report" data-testid="mentor-report">
      <div className="mb-8 rounded-md border border-border bg-surface px-5 py-4">
        <p className="text-xs font-semibold uppercase tracking-widest text-accent">
          Relatório Borderless
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-text-primary">
          Evidências de aprendizado
        </h1>
        <p className="mt-2 text-sm text-text-secondary">
          Mentores veem o que o aluno demonstrou — não achismos.
        </p>
      </div>

      <div className="mb-8 grid gap-4 rounded-md border border-border bg-surface-elevated p-5 sm:grid-cols-2">
        <div>
          <p className="text-xs uppercase tracking-widest text-text-muted">Aluno</p>
          <p className="mt-1 text-lg font-medium text-text-primary">{report.display_name}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-text-muted">Objetivo</p>
          <p className="mt-1 text-lg font-medium text-text-primary">{report.goal}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-text-muted">Trilha</p>
          <p className="mt-1 text-sm text-text-secondary">{report.track_title}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-text-muted">Perfil</p>
          <p className="mt-1 text-sm text-text-secondary">{report.profile_label}</p>
        </div>
      </div>

      {report.learner_gaps.length > 0 && (
        <div className="mb-8 rounded-md border border-warning/30 bg-warning/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-widest text-warning">
            Lacunas do diagnóstico inicial
          </p>
          <ul className="mt-3 flex flex-wrap gap-2">
            {report.learner_gaps.map((gap) => (
              <li
                key={gap}
                className="rounded-full border border-warning/40 bg-bg px-3 py-1 text-sm text-text-secondary"
              >
                {gap}
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.validations.length === 0 ? (
        <div className="rounded-md border border-dashed border-border bg-surface p-8 text-center">
          <p className="text-sm text-text-muted">
            Nenhuma validação registrada ainda. Peça ao aluno para validar um tópico na trilha.
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          {report.validations.map((entry) => (
            <ValidationCard key={`${entry.node_id}-${entry.score}`} entry={entry} />
          ))}
        </div>
      )}

      <div className="mt-8">
        <Link href="/roadmap">
          <Button variant="ghost">← Voltar à trilha</Button>
        </Link>
      </div>
    </div>
  );
}
