import { describe, expect, it } from "vitest";

import {
  plgStackIsPinned,
  plgStackPanelState,
  plgStackWheelAction,
} from "./plg-stack-wheel";

describe("plgStackIsPinned", () => {
  it("is pinned when the stack top has reached the header offset", () => {
    expect(plgStackIsPinned(56, 900)).toBe(true);
    expect(plgStackIsPinned(20, 900)).toBe(true);
  });

  it("is not pinned before the stack reaches the header", () => {
    expect(plgStackIsPinned(120, 900)).toBe(false);
  });
});

describe("plgStackWheelAction", () => {
  const pinnedTop = 40;
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

  it("ignores wheel input outside the pinned zone", () => {
    expect(plgStackWheelAction(100, 1, 3, 200, 900)).toBe("ignore");
  });
});

describe("plgStackPanelState", () => {
  it("marks only the active panel as active", () => {
    expect(plgStackPanelState(0, 1)).toBe("before");
    expect(plgStackPanelState(1, 1)).toBe("active");
    expect(plgStackPanelState(2, 1)).toBe("after");
  });
});
