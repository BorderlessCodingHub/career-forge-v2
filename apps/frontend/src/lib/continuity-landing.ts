export type ContinuitySpineNode = {
  node_id: string;
  status: string;
};

/** Node the Continuity link may open. A stale node opens the Roadmap instead. */
export function continuityOpenNodeId(
  nodes: ContinuitySpineNode[],
  requestedNodeId: string | null,
  fromContinuity: boolean,
): string | null {
  if (!fromContinuity) return requestedNodeId;
  const next = nodes.find(
    (node) => node.status !== "aprovado" && node.status !== "bloqueado",
  );
  if (requestedNodeId && next?.node_id === requestedNodeId) {
    return requestedNodeId;
  }
  return null;
}
