import { describe, expect, it } from "vitest";

import {
  formatLegacyMentorSummary,
  formatNodeTitleForDisplay,
  hasStructuredEvidence,
  humanizeNodeId,
} from "./format-node-title";

describe("humanizeNodeId", () => {
  it("strips node prefix and hyphens", () => {
    expect(humanizeNodeId("node-1-python-data-foundations")).toBe(
      "Python Data Foundations",
    );
  });
});

describe("formatNodeTitleForDisplay", () => {
  it("returns human title when distinct from node_id", () => {
    expect(
      formatNodeTitleForDisplay(
        "Fundamentos de Python para IA/ML",
        "node-1-python-data-foundations",
      ),
    ).toBe("Fundamentos de Python para IA/ML");
  });

  it("humanizes slug when title equals node_id", () => {
    expect(
      formatNodeTitleForDisplay(
        "node-1-python-data-foundations",
        "node-1-python-data-foundations",
      ),
    ).toBe("Python Data Foundations");
  });
});

describe("formatLegacyMentorSummary", () => {
  it("removes node id parenthetical and splits sentences", () => {
    const lines = formatLegacyMentorSummary(
      "Mock interview MCQ de Python (node-1-python-data-foundations) — 0/7 acertos. Revise as lacunas.",
    );
    expect(lines).toEqual([
      "Mock interview MCQ de Python — 0/7 acertos.",
      "Revise as lacunas.",
    ]);
  });
});

describe("hasStructuredEvidence", () => {
  it("is true when any structured field is present", () => {
    expect(
      hasStructuredEvidence({
        strengths: [],
        gaps: ["Errou pergunta 1"],
        recommended_intervention: "",
      }),
    ).toBe(true);
  });
});
