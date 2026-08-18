import { describe, expect, it } from "vitest";

import {
  PLG_PLAQUE_LABELS,
  PLG_PLAQUE_SECTION_IDS,
  plgPlaqueLabelIndex,
} from "./plg-plaque-spy";

describe("plgPlaqueLabelIndex", () => {
  it("stays on the first label when step tops are still below the anchor", () => {
    expect(plgPlaqueLabelIndex(200, [201, 800, 1200])).toBe(0);
    expect(plgPlaqueLabelIndex(200, [250, 900, 1400])).toBe(0);
  });

  it("advances as each stack step crosses the anchor", () => {
    expect(plgPlaqueLabelIndex(200, [199, 800, 1200])).toBe(0);
    expect(plgPlaqueLabelIndex(200, [120, 199, 1200])).toBe(1);
    expect(plgPlaqueLabelIndex(200, [50, 80, 199])).toBe(2);
  });

  it("steps down when scrolling back above the anchor", () => {
    expect(plgPlaqueLabelIndex(200, [50, 210, 900])).toBe(0);
    expect(plgPlaqueLabelIndex(200, [250, 900, 1400])).toBe(0);
  });
});

describe("plg plaque copy slots", () => {
  it("has one label per stack section", () => {
    expect(PLG_PLAQUE_LABELS).toHaveLength(PLG_PLAQUE_SECTION_IDS.length);
  });
});
