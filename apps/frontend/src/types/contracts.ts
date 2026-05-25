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
      graph: Array<{ node_id: string; status: SkillStatus; mastery_score: number }>;
    }
  | { type: "error"; message: string };

export type DiagnosisResponse = {
  profile: { label: string; track_id: string };
  strengths: string[];
  gaps: string[];
  starting_priorities: string[];
  estimated_mastery: Record<string, number>;
};
