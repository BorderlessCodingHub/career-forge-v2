import type { RoadmapForgeEvent } from "@/types/contracts";

export function parseForgeStreamEvent(raw: unknown): RoadmapForgeEvent | null {
  if (!raw || typeof raw !== "object") return null;
  const record = raw as Record<string, unknown>;
  if (typeof record.type !== "string") return null;
  return record as RoadmapForgeEvent;
}

export type ForgeStreamState = {
  events: RoadmapForgeEvent[];
};

export type ForgeStreamSideEffects = {
  onEvent?: (event: RoadmapForgeEvent) => void;
  onComplete?: (events: RoadmapForgeEvent[]) => void;
  onError?: (message: string) => void;
};

export function createInitialForgeStreamState(): ForgeStreamState {
  return { events: [] };
}

type Strategy = (
  event: RoadmapForgeEvent,
  state: ForgeStreamState,
  effects: ForgeStreamSideEffects,
) => ForgeStreamState;

const strategies: Partial<Record<RoadmapForgeEvent["type"], Strategy>> = {
  error: (event, state, effects) => {
    if (event.type !== "error") return state;
    effects.onError?.(event.message);
    return state;
  },

  graph_ready: (event, state, effects) => {
    if (event.type !== "graph_ready") return state;
    const events = [...state.events, event];
    effects.onEvent?.(event);
    effects.onComplete?.(events);
    return { events };
  },
};

function appendEvent(
  event: RoadmapForgeEvent,
  state: ForgeStreamState,
  effects: ForgeStreamSideEffects,
): ForgeStreamState {
  const events = [...state.events, event];
  effects.onEvent?.(event);
  return { events };
}

export function applyForgeStreamEvent(
  state: ForgeStreamState,
  event: RoadmapForgeEvent,
  effects: ForgeStreamSideEffects = {},
): ForgeStreamState {
  if (event.type === "error") {
    const strategy = strategies.error;
    return strategy ? strategy(event, state, effects) : state;
  }

  if (event.type === "graph_ready") {
    const strategy = strategies.graph_ready;
    return strategy ? strategy(event, state, effects) : appendEvent(event, state, effects);
  }

  return appendEvent(event, state, effects);
}
