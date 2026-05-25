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

export type YearsXpRange = "0-1" | "1-3" | "3-5" | "5+";

export type CvAttachment = {
  filename: string;
  size: number;
  mimeType: string;
  dataBase64: string;
};

export type OnboardingSession = {
  goalId: string | null;
  motivation: string;
  yearsXp: YearsXpRange | null;
  cvAttachment: CvAttachment | null;
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

export type ValidationStatus = "aprovado" | "revisar";

export type ValidationQuestion = {
  id: string;
  index: number;
  label: string;
  prompt: string;
  hint?: string | null;
  rubric_criterion: string;
};

export type ValidationQuestionsResponse = {
  node_id: string;
  node_title: string;
  node_icon: string;
  questions: ValidationQuestion[];
};

export type ValidationAnswer = {
  question_id: string;
  answer: string;
};

export type ValidationResponse = {
  score: number;
  status: ValidationStatus;
  strengths: string[];
  gaps: string[];
  next_action: string;
  mentor_summary: string;
};

export type ValidationRunResponse = {
  run_id: string;
  status: string;
  events: Array<Record<string, unknown>>;
  validation: ValidationResponse;
  node_id: string;
  node_status: string;
  mastery_score: number;
  plan_update?: PlanUpdateResponse | null;
  graph_patch?: GraphPatch | null;
  roadmap?: RoadmapResponse | null;
};

export type MockInterviewQuestion = ValidationQuestion & {
  phase: "base" | "gap_probe" | "scenario";
};

export type MockInterviewQuestionsResponse = {
  node_id: string;
  node_title: string;
  node_icon: string;
  total_questions: number;
  questions: MockInterviewQuestion[];
};

export type MockInterviewRunResponse = ValidationRunResponse;

export type TodayFocus = {
  node_id: string;
  title: string;
  duration_minutes: number;
  objective: string;
};

export type PlanUpdateResponse = {
  today_focus: TodayFocus;
  next_mission: string;
};

export type GraphPatch = {
  patches: Array<{
    node_id: string;
    status: SkillStatus;
    mastery_estimated: number;
    priority: string;
    rationale: string;
  }>;
  continue_research: boolean;
  summary: string;
};

export type MentorMessage = {
  role: "user" | "assistant";
  content: string;
};

export type MentorContextSnapshot = {
  recent_gaps: string[];
  recent_strengths: string[];
  failed_nodes: string[];
  current_node_status?: string | null;
  current_node_mastery?: number | null;
  validation_count: number;
  last_validation_feedback?: string | null;
};

export type MentorResponse = {
  reply: string;
  references: string[];
  context_snapshot: MentorContextSnapshot;
};

export type MentorRunResponse = {
  run_id: string;
  status: string;
  events: Array<Record<string, unknown>>;
  mentor: MentorResponse;
};

export type MentorReportValidationEntry = {
  node_id: string;
  node_title: string;
  score: number;
  status: ValidationStatus;
  strengths: string[];
  gaps: string[];
  mentor_summary: string;
  recommended_intervention: string;
  validated_at?: string | null;
};

export type MentorReportResponse = {
  user_id: string;
  display_name: string;
  goal: string;
  track_title: string;
  profile_label: string;
  validations: MentorReportValidationEntry[];
  learner_gaps: string[];
};
