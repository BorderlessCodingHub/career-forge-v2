/**
 * AI JSON contracts — mirror of apps/api/app/schemas (HAC-7).
 * Use with Zod at call sites when apps/web adds zod dependency.
 */

export type SkillStatus =
  | "bloqueado"
  | "recomendado"
  | "em_estudo"
  | "validar"
  | "aprovado"
  | "revisar";

export type Priority = "high" | "medium" | "low";

export type ValidationStatus = "aprovado" | "revisar";

export type ForgeRunStatus = "running" | "done" | "error";

export interface DiagnosisProfile {
  label: string;
  track_id: string;
  persona_slug?: string | null;
}

export interface DiagnosisResponse {
  profile: DiagnosisProfile;
  strengths: string[];
  gaps: string[];
  starting_priorities: string[];
  estimated_mastery: Record<string, number>;
}

export interface UserSkillNodePartial {
  node_id: string;
  title?: string | null;
  status?: SkillStatus;
  mastery_score?: number;
  priority?: Priority;
  rationale?: string | null;
}

export interface UserSkillNode {
  node_id: string;
  title?: string | null;
  status: SkillStatus;
  mastery_score: number;
  priority?: Priority;
  rationale?: string | null;
}

export type RoadmapForgeEvent =
  | { type: "reasoning_delta"; text: string; step: string }
  | { type: "artifact_found"; label: string; detail: string }
  | { type: "node_updated"; node: UserSkillNodePartial }
  | { type: "step_complete"; step: string; iteration: number }
  | { type: "graph_ready"; graph: UserSkillNode[] }
  | { type: "error"; message: string };

export interface NodePatch {
  node_id: string;
  status: SkillStatus;
  mastery_estimated: number;
  priority: Priority;
  rationale?: string;
}

export interface GraphPatch {
  patches: NodePatch[];
  continue_research: boolean;
  summary: string;
}

export interface ValidationResponse {
  score: number;
  status: ValidationStatus;
  strengths: string[];
  gaps: string[];
  next_action: string;
  mentor_summary: string;
}

export interface TodayFocus {
  node_id: string;
  title: string;
  duration_minutes: number;
  objective: string;
}

export interface PlanUpdateResponse {
  today_focus: TodayFocus;
  next_mission: string;
}

/** LangGraph accumulated state (serialized dicts at runtime). */
export interface SkillGraphState {
  user_id: string;
  profile: DiagnosisResponse;
  base_catalog: Record<string, unknown>[];
  accumulated_graph: UserSkillNode[];
  reasoning_log: { step: string; text: string; iteration?: number }[];
  artifacts: { label: string; detail: string; node_id?: string | null }[];
  iteration: number;
  max_iterations: number;
  status: ForgeRunStatus;
}
