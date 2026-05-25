import { readJson, readString, removeItems, writeJson, writeString } from "@/lib/session/storage";
import type { PlanUpdateResponse, RoadmapResponse } from "@/types/contracts";

const PLAN_KEY = "career-forge:adaptive-plan";
const ROADMAP_KEY = "career-forge:adaptive-roadmap";
const NODE_KEY = "career-forge:adaptive-node";

export type AdaptiveSession = {
  plan: PlanUpdateResponse;
  roadmap: RoadmapResponse;
  nodeId: string;
};

export function storeAdaptiveSession(session: AdaptiveSession): void {
  writeJson(PLAN_KEY, session.plan);
  writeJson(ROADMAP_KEY, session.roadmap);
  writeString(NODE_KEY, session.nodeId);
}

export function getAdaptiveSession(): AdaptiveSession | null {
  const plan = readJson<PlanUpdateResponse>(PLAN_KEY);
  const roadmap = readJson<RoadmapResponse>(ROADMAP_KEY);
  const nodeId = readString(NODE_KEY);
  if (!plan || !roadmap || !nodeId) return null;
  return { plan, roadmap, nodeId };
}

export function clearAdaptiveSession(): void {
  removeItems([PLAN_KEY, ROADMAP_KEY, NODE_KEY]);
}
