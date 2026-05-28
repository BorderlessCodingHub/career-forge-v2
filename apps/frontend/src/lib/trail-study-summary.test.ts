import { describe, expect, it } from "vitest";

import { computeTrailStudySummary } from "./trail-study-summary";
import type { RoadmapNode } from "@/types/contracts";

function node(partial: Partial<RoadmapNode> & Pick<RoadmapNode, "node_id">): RoadmapNode {
  return {
    node_id: partial.node_id,
    title: partial.title ?? partial.node_id,
    description: "",
    category: "cat",
    icon: "code",
    side: "left",
    sort_order: 0,
    prerequisites: [],
    outcomes: [],
    rubric: [],
    status: "recomendado",
    mastery_score: 0,
    rationale: null,
    tasks: partial.tasks ?? [],
    references: partial.references ?? [],
    checklist_total: partial.checklist_total ?? 0,
    checklist_completed: partial.checklist_completed ?? 0,
  };
}

describe("computeTrailStudySummary", () => {
  it("returns null when no checklist items exist", () => {
    expect(computeTrailStudySummary([node({ node_id: "a" })])).toBeNull();
  });

  it("summarizes topics with study progress", () => {
    const summary = computeTrailStudySummary([
      node({
        node_id: "a",
        tasks: [{ id: "t1", title: "T", done: true }],
        checklist_total: 1,
        checklist_completed: 1,
      }),
      node({
        node_id: "b",
        references: [{ id: "r1", title: "R", done: false }],
        checklist_total: 1,
        checklist_completed: 0,
      }),
    ]);
    expect(summary).toBe("1/2 tópicos com estudo iniciado");
  });
});
