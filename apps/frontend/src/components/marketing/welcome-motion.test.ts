import { describe, expect, it } from "vitest";

import {
  FORGE_MOCK_ITEM_DURATION_MS,
  FORGE_MOCK_ITEM_STAGGER_MS,
  WELCOME_DURATION_MS,
  WELCOME_STAGGER_MS,
  WELCOME_TRANSLATE_PX,
  forgeMockCardReadyMs,
  forgeMockFocusDelayMs,
  forgeMockNodeDelayMs,
  forgeMockStepDelayMs,
  forgeMockStepsPhaseStartMs,
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

describe("forge mock choreography (PLG landpage only)", () => {
  it("starts after hero card fade completes", () => {
    expect(forgeMockCardReadyMs()).toBe(
      staggerDelayMs(6) + WELCOME_DURATION_MS,
    );
    expect(forgeMockNodeDelayMs(0)).toBe(forgeMockCardReadyMs());
  });

  it("uses slower sequential timing than hero copy stagger", () => {
    expect(FORGE_MOCK_ITEM_STAGGER_MS).toBeGreaterThan(WELCOME_STAGGER_MS);
    expect(FORGE_MOCK_ITEM_DURATION_MS).toBeGreaterThan(WELCOME_DURATION_MS);
  });

  it("runs nodes → focus → steps in order", () => {
    expect(forgeMockNodeDelayMs(3)).toBeLessThan(forgeMockFocusDelayMs());
    expect(forgeMockFocusDelayMs()).toBeLessThan(forgeMockStepsPhaseStartMs());
    expect(forgeMockStepDelayMs(0)).toBe(forgeMockStepsPhaseStartMs());
    expect(forgeMockStepDelayMs(3)).toBeGreaterThan(forgeMockStepDelayMs(0));
  });
});
