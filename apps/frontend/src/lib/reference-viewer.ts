import type {
  RoadmapChecklistItem,
  RoadmapNode,
  RoadmapResponse,
} from "@/types/contracts";

export type ResolvedReferenceViewer = {
  node: RoadmapNode;
  reference: RoadmapChecklistItem;
  references: RoadmapChecklistItem[];
};

export function buildReferenceViewerHref(nodeId: string, itemId: string): string {
  const params = new URLSearchParams({ node: nodeId, item: itemId });
  return `/reference?${params.toString()}`;
}

export function resolveReferenceViewer(
  roadmap: RoadmapResponse,
  nodeId: string | null,
  itemId: string | null,
): ResolvedReferenceViewer | null {
  if (!nodeId || !itemId) return null;

  const node = roadmap.nodes.find((candidate) => candidate.node_id === nodeId);
  if (!node) return null;

  const reference = node.references.find((candidate) => candidate.id === itemId);
  if (!reference?.url || !isSafeReferenceUrl(reference.url)) return null;

  return { node, reference, references: node.references };
}

function isSafeReferenceUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}
