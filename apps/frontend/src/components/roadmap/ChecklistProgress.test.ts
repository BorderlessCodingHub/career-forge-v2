import { describe, expect, it } from "vitest";

import { getTrailChecklistProgressPct } from "./checklist-progress-stats";
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

describe("getTrailChecklistProgressPct", () => {
  it("returns null when no checklist items exist", () => {
    expect(getTrailChecklistProgressPct([node({ node_id: "a" })])).toBeNull();
  });

  it("pools items across topics (11+9+5=25)", () => {
    const pct = getTrailChecklistProgressPct([
      node({ node_id: "a", checklist_total: 11, checklist_completed: 4 }),
      node({ node_id: "b", checklist_total: 9, checklist_completed: 3 }),
      node({ node_id: "c", checklist_total: 5, checklist_completed: 3 }),
    ]);
    expect(pct).toBe(40);
  });

  it("uses item-weighted pool, not topic-average", () => {
    const pct = getTrailChecklistProgressPct([
      node({ node_id: "a", checklist_total: 1, checklist_completed: 1 }),
      node({ node_id: "b", checklist_total: 3, checklist_completed: 0 }),
    ]);
    expect(pct).toBe(25);
  });

  it("computes percent of done checklist items across nodes", () => {
    const pct = getTrailChecklistProgressPct([
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
      node({
        node_id: "c",
        tasks: [
          { id: "t2", title: "T2", done: true },
          { id: "t3", title: "T3", done: false },
        ],
        checklist_total: 2,
        checklist_completed: 1,
      }),
    ]);
    expect(pct).toBe(50);
  });
});
