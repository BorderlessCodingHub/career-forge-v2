import { describe, expect, it } from "vitest";

import { FORGE_MOCK_FOCUS_NODE_INDEX, FORGE_MOCK_NODES, FORGE_MOCK_STEPS, TRAIL_MOCK_NODES } from "./forge-product-mock-data";

describe("forge product mock (PLG /welcome/plg)", () => {
  it("illustrates the diagnose → forge → validate loop without live data", () => {
    expect(FORGE_MOCK_STEPS.map((s) => s.label)).toEqual([
      "Diagnosing profile",
      "Planning coverage",
      "Forging roadmap",
      "Ready to validate",
    ]);
    expect(FORGE_MOCK_STEPS.filter((s) => s.state === "live")).toHaveLength(1);
  });

  it("shows four goal-shaped spine nodes", () => {
    expect(FORGE_MOCK_NODES).toHaveLength(4);
  });

  it("focuses Agent tools as the marketing you-are-here node", () => {
    expect(FORGE_MOCK_NODES[FORGE_MOCK_FOCUS_NODE_INDEX]?.title).toBe(
      "Agent tools",
    );
    expect(FORGE_MOCK_NODES[FORGE_MOCK_FOCUS_NODE_INDEX]?.status).toBe(
      "validar",
    );
  });

  it("illustrates the artifact trail spine for the audience section", () => {
    expect(TRAIL_MOCK_NODES.map((n) => n.title)).toEqual(
      FORGE_MOCK_NODES.map((n) => n.title),
    );
    expect(TRAIL_MOCK_NODES[FORGE_MOCK_FOCUS_NODE_INDEX]?.side).toBe("right");
  });
});
