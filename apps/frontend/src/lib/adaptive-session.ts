import type { PlanUpdateResponse, RoadmapResponse } from "@/types/contracts";

const PLAN_KEY = "career-forge:adaptive-plan";
const ROADMAP_KEY = "career-forge:adaptive-roadmap";

export type AdaptiveSession = {
  plan: PlanUpdateResponse;
  roadmap: RoadmapResponse;
  nodeId: string;
};

export function storeAdaptiveSession(session: AdaptiveSession): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(PLAN_KEY, JSON.stringify(session.plan));
  window.sessionStorage.setItem(ROADMAP_KEY, JSON.stringify(session.roadmap));
  window.sessionStorage.setItem("career-forge:adaptive-node", session.nodeId);
}

export function getAdaptiveSession(): AdaptiveSession | null {
  if (typeof window === "undefined") return null;
  const planRaw = window.sessionStorage.getItem(PLAN_KEY);
  const roadmapRaw = window.sessionStorage.getItem(ROADMAP_KEY);
  const nodeId = window.sessionStorage.getItem("career-forge:adaptive-node");
  if (!planRaw || !roadmapRaw || !nodeId) return null;
  try {
    return {
      plan: JSON.parse(planRaw) as PlanUpdateResponse,
      roadmap: JSON.parse(roadmapRaw) as RoadmapResponse,
      nodeId,
    };
  } catch {
    return null;
  }
}

export function clearAdaptiveSession(): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.removeItem(PLAN_KEY);
  window.sessionStorage.removeItem(ROADMAP_KEY);
  window.sessionStorage.removeItem("career-forge:adaptive-node");
}
