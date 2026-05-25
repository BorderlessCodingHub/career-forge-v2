import { describe, expect, it } from "vitest";

import {
  applyForgeStreamEvent,
  createInitialForgeStreamState,
  parseForgeStreamEvent,
} from "@/lib/forge-stream";

describe("parseForgeStreamEvent", () => {
  it("accepts typed forge payloads", () => {
    expect(
      parseForgeStreamEvent({
        type: "step_complete",
        step: "load_topics",
        iteration: 1,
      }),
    ).toEqual({
      type: "step_complete",
      step: "load_topics",
      iteration: 1,
    });
  });
});

describe("applyForgeStreamEvent", () => {
  it("accumulates events and signals completion on graph_ready", () => {
    const seen: string[] = [];
    let completed: string[] | null = null;

    const state = createInitialForgeStreamState();
    const afterStep = applyForgeStreamEvent(
      state,
      { type: "step_complete", step: "load_topics", iteration: 1 },
      { onEvent: (event) => seen.push(event.type) },
    );

    applyForgeStreamEvent(
      afterStep,
      { type: "graph_ready", graph: [] },
      {
        onEvent: (event) => seen.push(event.type),
        onComplete: (events) => {
          completed = events.map((event) => event.type);
        },
      },
    );

    expect(seen).toEqual(["step_complete", "graph_ready"]);
    expect(completed).toEqual(["step_complete", "graph_ready"]);
  });

  it("routes error events to onError without appending", () => {
    let message: string | null = null;
    const next = applyForgeStreamEvent(
      createInitialForgeStreamState(),
      { type: "error", message: "boom" },
      { onError: (value) => { message = value; } },
    );

    expect(message).toBe("boom");
    expect(next.events).toHaveLength(0);
  });
});
