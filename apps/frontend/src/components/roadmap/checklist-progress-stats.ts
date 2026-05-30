import type { RoadmapNode } from "@/types/contracts";

export type ChecklistProgressStats = {
  total: number;
  completed: number;
  percent: number;
};

export function getChecklistProgress(node: RoadmapNode): ChecklistProgressStats {
  const total = node.checklist_total ?? node.tasks.length + node.references.length;
  const completed =
    node.checklist_completed ??
    [...node.tasks, ...node.references].filter((item) => item.done).length;
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
  return { total, completed, percent };
}

/** Item-pool trail % — same per-topic math as canvas bars, summed across all topics. */
export function getTrailChecklistProgressPct(nodes: RoadmapNode[]): number | null {
  let sumCompleted = 0;
  let sumTotal = 0;

  for (const node of nodes) {
    const { completed, total } = getChecklistProgress(node);
    sumCompleted += completed;
    sumTotal += total;
  }

  if (sumTotal === 0) return null;

  return Math.min(100, Math.max(0, Math.round((sumCompleted / sumTotal) * 100)));
}
