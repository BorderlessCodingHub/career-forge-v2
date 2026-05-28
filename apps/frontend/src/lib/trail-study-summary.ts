import type { RoadmapNode } from "@/types/contracts";

export function computeTrailStudySummary(nodes: RoadmapNode[]): string | null {
  const withChecklist = nodes.filter((node) => {
    const total =
      node.checklist_total ?? node.tasks.length + node.references.length;
    return total > 0;
  });

  if (withChecklist.length === 0) return null;

  const started = withChecklist.filter((node) => {
    const completed =
      node.checklist_completed ??
      [...node.tasks, ...node.references].filter((item) => item.done).length;
    return completed > 0;
  }).length;

  return `${started}/${withChecklist.length} tópicos com estudo iniciado`;
}
