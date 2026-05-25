import type {
  DiagnosisInterviewStatusPhase,
  DiagnosisStreamEvent,
  RubricDimensionKey,
  RubricDimensionStatus,
  RubricMapItem,
} from "@/types/contracts";

const PHASE_LABELS: Record<DiagnosisInterviewStatusPhase, string> = {
  analyzing_intake: "Lendo seu objetivo e motivação…",
  analyzing_cv: "Analisando currículo…",
  judging: "IA mapeando seu perfil…",
  loading_questions: "Preparando perguntas…",
  planning_questions: "Preparando perguntas…",
  processing_answers: "Processando suas respostas…",
  finalizing: "Gerando diagnóstico…",
};

const STATUS_RANK: Record<RubricDimensionStatus, number> = {
  pending: 0,
  needs_clarification: 1,
  mapped: 2,
};

export function diagnosisStreamPhaseLabel(
  phase: DiagnosisInterviewStatusPhase | null,
): string {
  if (!phase) return "Analisando seu perfil…";
  return PHASE_LABELS[phase];
}

export function isMappingItemDone(item: RubricMapItem): boolean {
  return item.saturated || item.status === "mapped";
}

function itemRank(item: RubricMapItem): number {
  if (isMappingItemDone(item)) return STATUS_RANK.mapped;
  return STATUS_RANK[item.status];
}

export function mergeMappingItem(
  previous: RubricMapItem,
  incoming: RubricMapItem,
): RubricMapItem {
  const previousDone = isMappingItemDone(previous);
  const incomingDone = isMappingItemDone(incoming);

  if (previousDone && !incomingDone) {
    return {
      ...previous,
      confidence: Math.max(previous.confidence, incoming.confidence),
      note: previous.note.trim() || incoming.note,
    };
  }

  const status =
    itemRank(incoming) >= itemRank(previous) ? incoming.status : previous.status;

  return {
    ...incoming,
    status,
    saturated: previous.saturated || incoming.saturated,
    confidence: Math.max(previous.confidence, incoming.confidence),
    note: incoming.note.trim() || previous.note,
  };
}

export function mergeMappingProgress(
  previous: RubricMapItem[],
  incoming: RubricMapItem[],
): RubricMapItem[] {
  const incomingByKey = new Map(incoming.map((item) => [item.rubric_key, item]));
  return previous.map(
    (item) => mergeMappingItem(item, incomingByKey.get(item.rubric_key) ?? item),
  );
}

export function applyMappingDimensionEvent(
  items: RubricMapItem[],
  event: Extract<DiagnosisStreamEvent, { type: "mapping_dimension" }>,
): RubricMapItem[] {
  return items.map((item) =>
    item.rubric_key === event.item.rubric_key
      ? mergeMappingItem(item, event.item)
      : item,
  );
}

export function nextAnalyzingKey(
  items: RubricMapItem[],
  current: RubricDimensionKey | null,
): RubricDimensionKey | null {
  const pending = items.filter((item) => !isMappingItemDone(item));
  if (pending.length === 0) return null;

  if (current) {
    const currentIndex = items.findIndex((item) => item.rubric_key === current);
    const after = items
      .slice(currentIndex + 1)
      .find((item) => !isMappingItemDone(item));
    if (after) return after.rubric_key;
  }

  return pending[0]?.rubric_key ?? null;
}

export function firstPendingAnalyzingKey(items: RubricMapItem[]): RubricDimensionKey | null {
  return items.find((item) => !isMappingItemDone(item))?.rubric_key ?? null;
}
