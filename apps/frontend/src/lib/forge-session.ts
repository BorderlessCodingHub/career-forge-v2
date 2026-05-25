import { readJson, removeItems, writeJson, writeString, readString } from "@/lib/session/storage";
import type { DiagnosisResponse, RoadmapForgeEvent } from "@/types/contracts";

const FORGE_GRAPH_KEY = "career-forge.forge-graph";
const FORGE_RUN_KEY = "career-forge.forge-run-id";

export type ForgeGraphNode = {
  node_id: string;
  title?: string;
  status: string;
  mastery_score: number;
  priority?: string;
  rationale?: string;
};

export function setForgeRunId(runId: string) {
  writeString(FORGE_RUN_KEY, runId);
}

export function getForgeRunId(): string | null {
  return readString(FORGE_RUN_KEY);
}

export function setForgeGraph(graph: ForgeGraphNode[]) {
  writeJson(FORGE_GRAPH_KEY, graph);
}

export function getForgeGraph(): ForgeGraphNode[] | null {
  return readJson<ForgeGraphNode[]>(FORGE_GRAPH_KEY);
}

export function extractGraphFromEvents(
  events: RoadmapForgeEvent[],
): ForgeGraphNode[] | null {
  const ready = events.find((e) => e.type === "graph_ready");
  if (!ready || ready.type !== "graph_ready") return null;
  return ready.graph.map((node) => ({
    node_id: node.node_id,
    title: "title" in node ? (node.title as string | undefined) : undefined,
    status: node.status,
    mastery_score: node.mastery_score,
  }));
}

export function diagnosisForForge(
  diagnosis: DiagnosisResponse,
): DiagnosisResponse {
  return diagnosis;
}

export function clearForgeSession() {
  removeItems([FORGE_GRAPH_KEY, FORGE_RUN_KEY]);
}
