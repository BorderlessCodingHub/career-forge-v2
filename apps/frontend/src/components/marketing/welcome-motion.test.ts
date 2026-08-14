import { describe, expect, it } from "vitest";

import {
  WELCOME_DURATION_MS,
  WELCOME_STAGGER_MS,
  WELCOME_TRANSLATE_PX,
  heroItemStyle,
  scrollRevealClassName,
  shouldSkipMotion,
  staggerDelayMs,
} from "./welcome-motion";

describe("welcome-motion constants (grill lock)", () => {
  it("keeps stagger and duration inside the lean palette band", () => {
    expect(WELCOME_STAGGER_MS).toBeGreaterThanOrEqual(40);
    expect(WELCOME_STAGGER_MS).toBeLessThanOrEqual(80);
    expect(WELCOME_DURATION_MS).toBeGreaterThanOrEqual(300);
    expect(WELCOME_DURATION_MS).toBeLessThanOrEqual(400);
    expect(WELCOME_TRANSLATE_PX).toBeLessThanOrEqual(8);
  });
});

describe("staggerDelayMs", () => {
  it("scales by index and stagger step", () => {
    expect(staggerDelayMs(0)).toBe(0);
    expect(staggerDelayMs(1)).toBe(WELCOME_STAGGER_MS);
    expect(staggerDelayMs(3)).toBe(3 * WELCOME_STAGGER_MS);
  });
});

describe("heroItemStyle", () => {
  it("sets animation-delay for CSS hero stagger without JS gating", () => {
    expect(heroItemStyle(2)).toEqual({
      animationDelay: `${2 * WELCOME_STAGGER_MS}ms`,
    });
  });
});

describe("scrollRevealClassName", () => {
  it("marks one-shot reveal visible state", () => {
    expect(scrollRevealClassName(false)).toBe("welcome-reveal");
    expect(scrollRevealClassName(true)).toBe("welcome-reveal is-visible");
  });
});

describe("shouldSkipMotion", () => {
  it("skips all motion when prefers-reduced-motion is on", () => {
    expect(shouldSkipMotion(true)).toBe(true);
    expect(shouldSkipMotion(false)).toBe(false);
  });
});
