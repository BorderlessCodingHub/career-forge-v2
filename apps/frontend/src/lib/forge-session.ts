import type {
  DiagnosisResponse,
  ForgeGraphNode,
  RoadmapForgeEvent,
} from "@/types/contracts";

export type { ForgeGraphNode };

const FORGE_GRAPH_KEY = "career-forge.forge-graph";
const FORGE_RUN_KEY = "career-forge.forge-run-id";

function readJson<T>(key: string): T | null {
  if (typeof window === "undefined") return null;
  const raw = window.sessionStorage.getItem(key);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function writeJson(key: string, value: unknown) {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(key, JSON.stringify(value));
}

export function setForgeRunId(runId: string) {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(FORGE_RUN_KEY, runId);
}

export function getForgeRunId(): string | null {
  if (typeof window === "undefined") return null;
  return window.sessionStorage.getItem(FORGE_RUN_KEY);
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

export function clearForgeSession() {
  if (typeof window === "undefined") return;
  window.sessionStorage.removeItem(FORGE_GRAPH_KEY);
  window.sessionStorage.removeItem(FORGE_RUN_KEY);
}
