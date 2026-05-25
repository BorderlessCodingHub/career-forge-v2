import { readJson, removeItem, removeItems, readString, writeJson, writeString } from "@/lib/session/storage";
import type {
  DiagnosisResponse,
  ForgeGraphNode,
  RoadmapForgeEvent,
} from "@/types/contracts";

export type { ForgeGraphNode };

const FORGE_GRAPH_KEY = "career-forge.forge-graph";
const FORGE_RUN_KEY = "career-forge.forge-run-id";

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
  return ready.graph;
}

export function diagnosisForForge(
  diagnosis: DiagnosisResponse,
): DiagnosisResponse {
  return diagnosis;
}

export function clearForgeGraph() {
  removeItem(FORGE_GRAPH_KEY);
}

export function clearForgeSession() {
  removeItems([FORGE_GRAPH_KEY, FORGE_RUN_KEY]);
}
