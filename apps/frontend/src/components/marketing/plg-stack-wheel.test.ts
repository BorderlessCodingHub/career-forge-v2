import { describe, expect, it } from "vitest";

import {
  plgStackIsPinned,
  plgStackPanelState,
  plgStackWheelAction,
} from "./plg-stack-wheel";

describe("plgStackIsPinned", () => {
  it("is pinned when the first fold is docked under the header", () => {
    expect(plgStackIsPinned(56, 900)).toBe(true);
    expect(plgStackIsPinned(40, 900)).toBe(true);
  });

  it("is not pinned before the stage reaches the header", () => {
    expect(plgStackIsPinned(120, 900)).toBe(false);
  });

  it("is not pinned after the first fold has scrolled away", () => {
    expect(plgStackIsPinned(-80, 751)).toBe(false);
    expect(plgStackIsPinned(-318, 500)).toBe(false);
  });
});

describe("plgStackWheelAction", () => {
  const pinnedTop = 56;
  const pinnedBottom = 900;

  it("advances and retreats inside the stack without releasing scroll", () => {
    expect(
      plgStackWheelAction(100, 0, 3, pinnedTop, pinnedBottom),
    ).toBe("advance");
    expect(
      plgStackWheelAction(-100, 2, 3, pinnedTop, pinnedBottom),
    ).toBe("retreat");
  });

  it("releases scroll at the first and last steps", () => {
    expect(
      plgStackWheelAction(-100, 0, 3, pinnedTop, pinnedBottom),
    ).toBe("release-up");
    expect(
      plgStackWheelAction(100, 2, 3, pinnedTop, pinnedBottom),
    ).toBe("release-down");
  });

  it("ignores wheel input when the first fold is not docked", () => {
    expect(plgStackWheelAction(100, 1, 3, 200, 900)).toBe("ignore");
    expect(plgStackWheelAction(100, 1, 3, -200, 631)).toBe("ignore");
  });
});

describe("plgStackPanelState", () => {
  it("marks only the active panel as active", () => {
    expect(plgStackPanelState(0, 1)).toBe("before");
    expect(plgStackPanelState(1, 1)).toBe("active");
    expect(plgStackPanelState(2, 1)).toBe("after");
  });
});
