import type {
  RoadmapChecklistItem,
  RoadmapNode,
  RoadmapResponse,
} from "@/types/contracts";

export const REFERENCE_PREVIEW_SANDBOX = "allow-forms allow-popups allow-scripts";
export const REFERENCE_PREVIEW_REFERRER_POLICY = "no-referrer";

export type ResolvedReferenceViewer = {
  node: RoadmapNode;
  reference: RoadmapChecklistItem & { url: string };
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
  if (!reference || !hasSafeReferenceUrl(reference)) return null;

  return { node, reference, references: node.references };
}

export function getReferenceHostname(value: string): string {
  try {
    return new URL(value).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

export function isEmbeddableReferenceUrl(
  value: string,
  allowedDomains: readonly string[],
): boolean {
  if (!isSafeReferenceUrl(value)) return false;

  const hostname = getReferenceHostname(value).toLowerCase().replace(/\.$/, "");
  if (!hostname) return false;

  return allowedDomains.some((domain) => {
    const normalizedDomain = domain
      .toLowerCase()
      .replace(/^www\./, "")
      .replace(/\.$/, "");
    if (!normalizedDomain) return false;
    return hostname === normalizedDomain || hostname.endsWith(`.${normalizedDomain}`);
  });
}

function hasSafeReferenceUrl(
  reference: RoadmapChecklistItem,
): reference is RoadmapChecklistItem & { url: string } {
  return Boolean(reference.url && isSafeReferenceUrl(reference.url));
}

function isSafeReferenceUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}
