"use client";

import Link from "next/link";
import { useState } from "react";

import { ChecklistProgress, getChecklistProgress } from "@/components/roadmap/ChecklistProgress";
import { Button } from "@/components/ui";
import type { RoadmapChecklistItem, RoadmapNode } from "@/types/contracts";

type NodeDrawerProps = {
  node: RoadmapNode | null;
  onClose: () => void;
  onOpenMentor: () => void;
  onChecklistToggle?: (
    nodeId: string,
    itemType: "task" | "reference",
    itemId: string,
    done: boolean,
  ) => Promise<void>;
};

const STATUS_LABELS: Record<string, string> = {
  bloqueado: "Bloqueado",
  recomendado: "Recomendado",
  em_estudo: "Em estudo",
  validar: "Validar",
  aprovado: "Aprovado",
  revisar: "Revisar",
};

export function NodeDrawer({ node, onClose, onOpenMentor, onChecklistToggle }: NodeDrawerProps) {
  const [pendingItemId, setPendingItemId] = useState<string | null>(null);

  if (!node) return null;

  const nodeId = node.node_id;
  const { total: checklistTotal } = getChecklistProgress(node);
  const showChecklistProgress = checklistTotal > 0;

  async function handleToggle(
    itemType: "task" | "reference",
    item: RoadmapChecklistItem,
    nextDone: boolean,
  ) {
    if (!onChecklistToggle) return;
    setPendingItemId(item.id);
    try {
      await onChecklistToggle(nodeId, itemType, item.id, nextDone);
    } finally {
      setPendingItemId(null);
    }
  }

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
            aria-label="Fechar detalhes"
            onClick={onClose}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-sm font-medium text-red-400 transition-all duration-200 hover:bg-red-900/60 hover:text-red-300 focus-visible:bg-red-900/60 focus-visible:text-red-300 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-red-500/50 active:bg-red-800/60"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 space-y-6 overflow-y-auto px-6 py-5">

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

          {showChecklistProgress && <ChecklistProgress variant="full" node={node} />}

          {node.rationale && (
            <div className="rounded-md border border-accent/30 bg-accent/10 bg-surface px-3 py-2 text-sm text-text-primary">
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
                {node.tasks.map((task) => (
                  <li
                    key={task.id}
                    className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-secondary"
                  >
                    <label className="flex cursor-pointer items-start gap-3">
                      <input
                        type="checkbox"
                        className="mt-1 h-4 w-4 rounded border-border accent-accent-mint"
                        checked={task.done}
                        disabled={!onChecklistToggle || pendingItemId === task.id}
                        onChange={(event) =>
                          void handleToggle("task", task, event.target.checked)
                        }
                        data-testid={`checklist-task-${task.id}`}
                      />
                      <span className={task.done ? "opacity-70 line-through" : undefined}>
                        <p className="font-medium text-text-primary">
                          {task.title ?? "Tarefa prática"}
                        </p>
                        {task.outcome && <p className="mt-1">{task.outcome}</p>}
                        {task.evidence_prompt && (
                          <p className="mt-1 text-xs text-accent-mint">
                            Evidência: {task.evidence_prompt}
                          </p>
                        )}
                      </span>
                    </label>
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
                {node.references.map((reference) => (
                  <div
                    key={reference.id}
                    className="rounded-md border border-border bg-surface px-3 py-2 text-sm transition hover:border-accent/60 hover:bg-surface-elevated"
                  >
                    <label className="flex cursor-pointer items-start gap-3">
                      <input
                        type="checkbox"
                        className="mt-1 h-4 w-4 rounded border-border accent-accent-mint"
                        checked={reference.done}
                        disabled={!onChecklistToggle || pendingItemId === reference.id}
                        onChange={(event) =>
                          void handleToggle("reference", reference, event.target.checked)
                        }
                        data-testid={`checklist-reference-${reference.id}`}
                      />
                      <span className={reference.done ? "opacity-70" : undefined}>
                        {reference.url ? (
                          <a
                            href={reference.url}
                            target="_blank"
                            rel="noreferrer"
                            className="font-medium text-text-primary underline-offset-2 hover:underline"
                            onClick={(event) => event.stopPropagation()}
                          >
                            {reference.title ?? "Referência"}
                          </a>
                        ) : (
                          <span className="font-medium text-text-primary">
                            {reference.title ?? "Referência"}
                          </span>
                        )}
                        {reference.url && (
                          <span className="mt-1 block text-xs text-accent-mint">
                            {hostname(reference.url)}
                          </span>
                        )}
                      </span>
                    </label>
                  </div>
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
