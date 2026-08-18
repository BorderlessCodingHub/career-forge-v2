import { describe, expect, it } from "vitest";

import {
  PLG_PLAQUE_LABELS,
  PLG_PLAQUE_SECTION_IDS,
  plgPlaqueLabelIndex,
} from "./plg-plaque-spy";

describe("plgPlaqueLabelIndex", () => {
  it("stays on the rest label when section tops are still below the plaque", () => {
    expect(plgPlaqueLabelIndex(200, [200, 800])).toBe(0);
    expect(plgPlaqueLabelIndex(200, [201, 800])).toBe(0);
  });

  it("selects a section once its top crosses the plaque bottom", () => {
    expect(plgPlaqueLabelIndex(200, [199, 800])).toBe(1);
    expect(plgPlaqueLabelIndex(200, [120, 199])).toBe(2);
  });

  it("uses the last crossed section when scrolling back", () => {
    expect(plgPlaqueLabelIndex(200, [50, 210])).toBe(1);
    expect(plgPlaqueLabelIndex(200, [250, 900])).toBe(0);
  });
});

describe("plg plaque copy slots", () => {
  it("has one rest label plus one label per spy section", () => {
    expect(PLG_PLAQUE_LABELS).toHaveLength(PLG_PLAQUE_SECTION_IDS.length + 1);
  });
});
