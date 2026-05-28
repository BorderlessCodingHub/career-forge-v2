"use client";

import Link from "next/link";

import { Button } from "@/components/ui";
import type { RoadmapNode } from "@/types/contracts";

type NodeDrawerProps = {
  node: RoadmapNode | null;
  onClose: () => void;
  onOpenMentor: () => void;
};

const STATUS_LABELS: Record<string, string> = {
  bloqueado: "Bloqueado",
  recomendado: "Recomendado",
  em_estudo: "Em estudo",
  validar: "Validar",
  aprovado: "Aprovado",
  revisar: "Revisar",
};

export function NodeDrawer({ node, onClose, onOpenMentor }: NodeDrawerProps) {
  if (!node) return null;

  return (
    <>
      <button
        type="button"
        aria-label="Fechar detalhes"
        className="fixed inset-0 z-40 bg-black/40"
        onClick={onClose}
        data-testid="node-drawer-backdrop"
      />
      <aside
        className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-border bg-surface-elevated shadow-xl"
        data-testid="node-drawer"
      >
        <div className="flex items-start justify-between border-b border-border px-6 py-5">
          <div>
            <p className="text-xs uppercase tracking-widest text-text-muted">{node.category}</p>
            <h2 className="mt-1 text-xl font-semibold text-text-primary">{node.title}</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-2 py-1 text-text-muted hover:bg-surface hover:text-text-primary"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 space-y-6 overflow-y-auto px-6 py-5">
          <p className="text-sm text-text-secondary">{node.description}</p>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-md border border-border bg-surface px-3 py-2">
              <p className="text-xs text-text-muted">Status</p>
              <p className="font-medium text-text-primary">
                {STATUS_LABELS[node.status] ?? node.status}
              </p>
            </div>
            <div className="rounded-md border border-border bg-surface px-3 py-2">
              <p className="text-xs text-text-muted">Mastery</p>
              <p className="font-mono font-medium text-accent-mint">{node.mastery_score}%</p>
            </div>
          </div>

          {node.rationale && (
            <div className="rounded-md border border-accent/30 bg-accent/10 px-3 py-2 text-sm text-text-secondary">
              {node.rationale}
            </div>
          )}

          {node.outcomes.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest text-text-muted">
                Resultados esperados
              </h3>
              <ul className="mt-2 space-y-2">
                {node.outcomes.map((outcome) => (
                  <li
                    key={outcome}
                    className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-secondary"
                  >
                    {outcome}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {node.tasks.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest text-text-muted">
                Tarefas práticas
              </h3>
              <ul className="mt-2 space-y-2">
                {node.tasks.map((task, index) => (
                  <li
                    key={`${task.title}-${index}`}
                    className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-secondary"
                  >
                    <p className="font-medium text-text-primary">{task.title}</p>
                    {task.outcome && <p className="mt-1">{task.outcome}</p>}
                    {task.evidence_prompt && (
                      <p className="mt-1 text-xs text-accent-mint">
                        Evidência: {task.evidence_prompt}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {node.references.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest text-text-muted">
                Referências
              </h3>
              <div className="mt-2 space-y-2">
                {node.references.map((reference, index) => (
                  <a
                    key={`${reference.url}-${index}`}
                    href={reference.url}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-md border border-border bg-surface px-3 py-2 text-sm transition hover:border-accent/60 hover:bg-surface-elevated"
                  >
                    <span className="font-medium text-text-primary">
                      {reference.title}
                    </span>
                    {reference.url && (
                      <span className="mt-1 block text-xs text-accent-mint">
                        {hostname(reference.url)}
                      </span>
                    )}
                  </a>
                ))}
              </div>
            </div>
          )}

          <div>
            <h3 className="text-xs font-semibold uppercase tracking-widest text-text-muted">
              Mentor contextual
            </h3>
            <p className="mt-2 text-sm text-text-secondary">
              Peça referências, esclareça lacunas da validação ou como praticar este tópico.
            </p>
            <Button
              variant="ghost"
              className="mt-3"
              onClick={onOpenMentor}
              data-testid="open-mentor-drawer"
            >
              Abrir chat com mentor →
            </Button>
          </div>
        </div>

        <div className="border-t border-border px-6 py-4">
          <Link href={`/validate?node=${node.node_id}&mode=loop`}>
            <Button className="w-full" data-testid="validate-node-cta">
              Mock interview — validar mastery →
            </Button>
          </Link>
        </div>
      </aside>
    </>
  );
}

function hostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}
