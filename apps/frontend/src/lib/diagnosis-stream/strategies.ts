import {
  applyMappingDimensionEvent,
  firstPendingAnalyzingKey,
  mergeMappingProgress,
  nextAnalyzingKey,
} from "@/lib/diagnosis-stream/state";
import type {
  DiagnosisInterviewStatusPhase,
  DiagnosisStreamEvent,
  InterviewTurnResponse,
  RubricDimensionKey,
  RubricMapItem,
} from "@/types/contracts";
import { buildSkeletonMappingProgress } from "@/lib/profile-dimensions";

export type DiagnosisStreamUiState = {
  streamPhase: DiagnosisInterviewStatusPhase | null;
  analyzingKey: RubricDimensionKey | null;
  mappingProgress: RubricMapItem[];
};

export type DiagnosisStreamSideEffects = {
  onComplete?: (output: InterviewTurnResponse) => void;
  onError?: (message: string) => void;
};

export function createInitialDiagnosisStreamState(): DiagnosisStreamUiState {
  return {
    streamPhase: null,
    analyzingKey: null,
    mappingProgress: buildSkeletonMappingProgress(),
  };
}

type Strategy = (
  event: DiagnosisStreamEvent,
  state: DiagnosisStreamUiState,
  effects: DiagnosisStreamSideEffects,
) => DiagnosisStreamUiState;

const strategies: Partial<Record<DiagnosisStreamEvent["type"], Strategy>> = {
  interview_status: (event, state) => {
    if (event.type !== "interview_status") return state;
    return {
      ...state,
      streamPhase: event.phase,
      analyzingKey:
        event.phase === "judging"
          ? state.analyzingKey ?? firstPendingAnalyzingKey(state.mappingProgress)
          : state.analyzingKey,
    };
  },

  mapping_dimension: (event, state) => {
    if (event.type !== "mapping_dimension") return state;
    const mappingProgress = applyMappingDimensionEvent(state.mappingProgress, event);
    return {
      ...state,
      mappingProgress,
      analyzingKey: nextAnalyzingKey(mappingProgress, event.item.rubric_key),
    };
  },

  graph_complete: (event, _state, effects) => {
    if (event.type !== "graph_complete") return _state;
    effects.onComplete?.(event.output);
    return _state;
  },

  error: (event, state, effects) => {
    if (event.type !== "error") return state;
    effects.onError?.(event.message);
    return state;
  },
};

export function applyDiagnosisStreamEvent(
  state: DiagnosisStreamUiState,
  event: DiagnosisStreamEvent,
  effects: DiagnosisStreamSideEffects = {},
): DiagnosisStreamUiState {
  const strategy = strategies[event.type];
  if (!strategy) return state;
  return strategy(event, state, effects);
}

export function hydrateMappingFromResponse(
  response: InterviewTurnResponse,
  previous?: RubricMapItem[],
): RubricMapItem[] {
  const skeleton = buildSkeletonMappingProgress();
  const base =
    previous && previous.length === skeleton.length ? previous : skeleton;
  return mergeMappingProgress(base, response.mapping_progress);
}
