import type {
  DiagnosisInterviewStatusPhase,
  DiagnosisStreamEvent,
  RubricDimensionKey,
  RubricMapItem,
} from "@/types/contracts";

const PHASE_LABELS: Record<DiagnosisInterviewStatusPhase, string> = {
  analyzing_intake: "Lendo seu objetivo e motivação…",
  analyzing_cv: "Analisando currículo…",
  judging: "IA mapeando seu perfil…",
  planning_questions: "Preparando perguntas…",
  processing_answers: "Processando suas respostas…",
  finalizing: "Gerando diagnóstico…",
};

export function diagnosisStreamPhaseLabel(
  phase: DiagnosisInterviewStatusPhase | null,
): string {
  if (!phase) return "Analisando seu perfil…";
  return PHASE_LABELS[phase];
}

export function applyMappingDimensionEvent(
  items: RubricMapItem[],
  event: Extract<DiagnosisStreamEvent, { type: "mapping_dimension" }>,
): RubricMapItem[] {
  return items.map((item) =>
    item.rubric_key === event.item.rubric_key ? event.item : item,
  );
}

export function nextAnalyzingKey(
  items: RubricMapItem[],
  current: RubricDimensionKey | null,
): RubricDimensionKey | null {
  const pending = items.filter(
    (item) => item.status === "pending" && item.rubric_key !== current,
  );
  if (pending.length === 0) return null;
  if (current) {
    const currentIndex = items.findIndex((item) => item.rubric_key === current);
    const after = items.slice(currentIndex + 1).find((item) => item.status === "pending");
    if (after) return after.rubric_key;
  }
  return pending[0]?.rubric_key ?? null;
}
