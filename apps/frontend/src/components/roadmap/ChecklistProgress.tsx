import type { RoadmapNode } from "@/types/contracts";

import { getChecklistProgress } from "./checklist-progress-stats";

export type { ChecklistProgressStats } from "./checklist-progress-stats";
export { getChecklistProgress, getTrailChecklistProgressPct } from "./checklist-progress-stats";

type ChecklistProgressProps = {
  node: RoadmapNode;
  variant: "compact" | "full";
};

export function ChecklistProgress({ node, variant }: ChecklistProgressProps) {
  const { total, completed, percent } = getChecklistProgress(node);
  if (total <= 0) return null;

  const progressBar = (
    <div
      className={
        variant === "compact"
          ? "h-1.5 overflow-hidden rounded-full bg-surface-elevated/80"
          : "mt-2 h-2 overflow-hidden rounded-full bg-surface-elevated"
      }
      role="progressbar"
      aria-valuenow={completed}
      aria-valuemin={0}
      aria-valuemax={total}
    >
      <div
        className="h-full rounded-full bg-accent-mint transition-all"
        style={{ width: `${percent}%` }}
      />
    </div>
  );

  if (variant === "compact") {
    return (
      <div className="space-y-1">
        <div className="flex items-center justify-end">
          <span className="font-mono text-[10px] text-text-muted">
            {completed}/{total}
          </span>
        </div>
        {progressBar}
      </div>
    );
  }

  return (
    <div
      className="rounded-md border border-border bg-surface px-3 py-3"
      data-testid="node-checklist-progress"
    >
      <div className="flex items-center justify-between text-xs text-text-muted">
        <span>Progresso de estudo</span>
        <span className="font-mono text-text-primary">
          {completed}/{total} concluídos
        </span>
      </div>
      {progressBar}
      <p className="mt-2 text-xs text-text-muted" data-testid="checklist-non-blocking-copy">
        Marcar leitura e prática ajuda a acompanhar o estudo — é opcional e não substitui a
        validação por IA. A prova real de mastery continua sendo o mock interview.
      </p>
    </div>
  );
}
