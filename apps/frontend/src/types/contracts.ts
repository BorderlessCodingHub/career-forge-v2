/** Mirror of backend HAC-7 Pydantic contracts (SSE union + diagnosis). */

export type SkillStatus =
  | "bloqueado"
  | "recomendado"
  | "em_estudo"
  | "validar"
  | "aprovado"
  | "revisar";

/** Dynamic per-user skill state — mirrors backend UserSkillNode. */
export type RoadmapSyncNode = {
  node_id: string;
  title?: string | null;
  status: SkillStatus;
  mastery_score: number;
  priority?: string | null;
  rationale?: string | null;
  prerequisites?: string[];
  tasks?: Array<Record<string, string>>;
  references?: Array<Record<string, string>>;
};

/** Forge session graph node — same contract as RoadmapSyncNode. */
export type ForgeGraphNode = RoadmapSyncNode;

export type RoadmapForgeEvent =
  | { type: "reasoning_delta"; text: string; step: string }
  | {
      type: "artifact_found";
      label: string;
      detail: string;
      sources?: Array<{ title: string; url: string; snippet?: string }>;
    }
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
      graph: RoadmapSyncNode[];
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

export type RoadmapChecklistItem = {
  id: string;
  done: boolean;
  title?: string;
  outcome?: string;
  evidence_prompt?: string;
  url?: string;
  source?: string;
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
  tasks: RoadmapChecklistItem[];
  references: RoadmapChecklistItem[];
  checklist_completed: number;
  checklist_total: number;
};

export type ChecklistToggleRequest = {
  user_id?: string;
  item_type: "task" | "reference";
  item_id: string;
  done: boolean;
};

export type RoadmapResponse = {
  track: RoadmapTrack;
  categories: RoadmapCategory[];
  nodes: RoadmapNode[];
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

export type MockInterviewOption = {
  letter: "A" | "B" | "C" | "D";
  text: string;
};

export type MockInterviewQuestion = ValidationQuestion & {
  phase: "base" | "gap_probe" | "scenario";
  options?: MockInterviewOption[] | null;
};

export type MockInterviewQuestionsResponse = {
  node_id: string;
  node_title: string;
  node_icon: string;
  session_id?: string | null;
  format?: "open" | "mcq";
  total_questions: number;
  questions: MockInterviewQuestion[];
};

export type MockInterviewRunResponse = ValidationRunResponse & {
  run_id?: string | null;
};

export type MockInterviewRequest = ValidationRequest & {
  session_id?: string | null;
};

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

export type TutorMessage = {
  role: "user" | "assistant";
  content: string;
};

export type TutorReference = {
  title: string;
  url?: string | null;
};

export type TutorContext = {
  node_id?: string | null;
  node_title?: string | null;
  key_concepts: string[];
  references: TutorReference[];
  open_gaps: string[];
};

export type TutorRequest = {
  user_id?: string;
  message: string;
  node_id?: string | null;
  node_title?: string | null;
  history?: TutorMessage[];
};

export type TutorResponse = {
  reply: string;
  references: string[];
  used_concepts: string[];
  context: TutorContext;
};

export type TutorRunResponse = {
  run_id: string;
  status: string;
  events: Array<Record<string, unknown>>;
  tutor: TutorResponse;
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

/** Universal profile dimension keys — mirrors backend PROFILE_DIMENSION_KEYS (ADR-002). */
export type RubricDimensionKey =
  | "motivation_goal"
  | "background_transfer"
  | "learning_velocity"
  | "hands_on_proof"
  | "constraints";

/** Ordered profile keys — must match backend PROFILE_DIMENSION_KEYS. */
export const PROFILE_DIMENSION_KEYS = [
  "motivation_goal",
  "background_transfer",
  "learning_velocity",
  "hands_on_proof",
  "constraints",
] as const satisfies readonly RubricDimensionKey[];

export type InterviewQuestion = {
  id: string;
  topic: string;
  rubric_key: RubricDimensionKey;
  question: string;
  example_of_answer: string;
};

export type InterviewAnswer = {
  question_id: string;
  text: string;
};

export type RubricDimensionStatus = "pending" | "mapped" | "needs_clarification";

export type RubricMapItem = {
  rubric_key: RubricDimensionKey;
  label: string;
  description: string;
  confidence: number;
  saturated: boolean;
  status: RubricDimensionStatus;
  note: string;
};

export type DiagnosisInterviewCvAttachment = {
  filename: string;
  mime_type: "application/pdf";
  content_base64: string;
  extracted_text?: string | null;
};

export type DiagnosisIntake = {
  user_id?: string;
  goal_id: string;
  motivation: string;
  years_xp?: YearsXpRange;
  cv?: DiagnosisInterviewCvAttachment;
};

export type InterviewTurnRequest = {
  answers: InterviewAnswer[];
};

export type InterviewTurnResponse = {
  session_id: string;
  status: "asking" | "complete";
  round_count: number;
  questions: InterviewQuestion[];
  mapping_progress: RubricMapItem[];
  diagnosis?: DiagnosisResponse;
};

export type DiagnosisInterviewStatusPhase =
  | "analyzing_intake"
  | "analyzing_cv"
  | "judging"
  | "loading_questions"
  | "planning_questions"
  | "processing_answers"
  | "finalizing";

export type DiagnosisStreamEvent =
  | { type: "interview_status"; phase: DiagnosisInterviewStatusPhase }
  | {
      type: "mapping_dimension";
      item: RubricMapItem;
      index: number;
      total: number;
    }
  | {
      type: "graph_complete";
      graph_name: string;
      output: InterviewTurnResponse & { session?: unknown };
    }
  | { type: "error"; message: string };

export type ForgeRunResponse = {
  run_id: string;
  status: string;
  events: Array<Record<string, unknown>>;
  output: Record<string, unknown> | null;
};

export type DiagnosisConfirmResponse = {
  user_id: string;
  profile_id: string;
  status: "confirmed";
};

export type KnowledgeGapItem = {
  concept: string;
  severity: "low" | "medium" | "high";
  status: "open" | "resolved";
  suggested_remediation: string | null;
  skill_node_id: string;
  updated_at: string | null;
};

export type ValidationRequest = {
  user_id?: string;
  node_id: string;
  node_title: string;
  rubric: string[];
  answers: ValidationAnswer[];
};

export type DemoValidationSummary = {
  node_id: string;
  score: number;
  passed: boolean;
  feedback?: string | null;
};

export type MentorRequest = {
  user_id?: string;
  message: string;
  node_id?: string | null;
  node_title?: string | null;
  history?: MentorMessage[];
};
