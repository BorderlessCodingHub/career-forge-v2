/** Mirror of backend HAC-7 Pydantic contracts (SSE union + diagnosis). */

export type SkillStatus =
  | "bloqueado"
  | "recomendado"
  | "em_estudo"
  | "validar"
  | "aprovado"
  | "revisar";

export type RoadmapForgeEvent =
  | { type: "reasoning_delta"; text: string; step: string }
  | { type: "artifact_found"; label: string; detail: string }
  | {
      type: "node_updated";
      node: {
        node_id: string;
        status?: SkillStatus;
        mastery_score?: number;
      };
    }
  | { type: "step_complete"; step: string; iteration: number }
  | {
      type: "graph_ready";
      graph: Array<{
        node_id: string;
        title?: string;
        status: SkillStatus;
        mastery_score: number;
        priority?: string;
        rationale?: string;
      }>;
    }
  | { type: "error"; message: string };

export type DiagnosisResponse = {
  profile: { label: string; track_id: string; persona_slug?: string | null };
  strengths: string[];
  gaps: string[];
  starting_priorities: string[];
  estimated_mastery: Record<string, number>;
};

export type OnboardingSession = {
  goalId: string;
  motivation: string;
  answers: Record<string, string>;
  diagnosis?: DiagnosisResponse;
};

export type RoadmapTrack = {
  id: string;
  title: string;
  description?: string;
};

export type RoadmapCategory = {
  id: string;
  label: string;
};

export type RoadmapNode = {
  node_id: string;
  title: string;
  category: string;
  description: string;
  icon: string;
  side: "left" | "right";
  sort_order: number;
  prerequisites: string[];
  outcomes: string[];
  rubric: string[];
  status: SkillStatus;
  mastery_score: number;
  priority?: string | null;
  rationale?: string | null;
};

export type RoadmapResponse = {
  track: RoadmapTrack;
  categories: RoadmapCategory[];
  nodes: RoadmapNode[];
};

export type RoadmapSyncNode = {
  node_id: string;
  title: string;
  status: SkillStatus | string;
  mastery_score: number;
  priority?: string | null;
  rationale?: string | null;
};
