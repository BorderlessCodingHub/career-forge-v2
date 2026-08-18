import type { CSSProperties } from "react";

/** Grill CAR-38: stagger 40–80ms */
export const WELCOME_STAGGER_MS = 60;

/** Grill CAR-38: duration 300–400ms */
export const WELCOME_DURATION_MS = 360;

/** Grill CAR-38: translateY ≤8px */
export const WELCOME_TRANSLATE_PX = 8;

export function staggerDelayMs(index: number): number {
  return index * WELCOME_STAGGER_MS;
}

/** CSS animation-delay for hero load stagger (SSR-safe; no JS gate). */
export function heroItemStyle(index: number): CSSProperties {
  return { animationDelay: `${staggerDelayMs(index)}ms` };
}

export function scrollRevealClassName(visible: boolean): string {
  return visible ? "welcome-reveal is-visible" : "welcome-reveal";
}

export function shouldSkipMotion(prefersReducedMotion: boolean): boolean {
  return prefersReducedMotion;
}

/** PLG `ForgeProductMock` — landpage illustration only; not product forge SSE. */
export const FORGE_MOCK_HERO_INDEX = 6;

export const FORGE_MOCK_NODE_COUNT = 4;
export const FORGE_MOCK_STEP_COUNT = 4;

/** Slower than CAR-38 hero copy — sequential illustration, not a load snap. */
export const FORGE_MOCK_ITEM_STAGGER_MS = 240;
export const FORGE_MOCK_ITEM_DURATION_MS = 880;
export const FORGE_MOCK_TRANSLATE_PX = 6;
export const FORGE_MOCK_PAUSE_BEFORE_FOCUS_MS = 420;
export const FORGE_MOCK_FOCUS_DURATION_MS = 640;
export const FORGE_MOCK_PAUSE_BEFORE_STEPS_MS = 380;

/** Hero card fade complete — internal mock choreography starts here. */
export function forgeMockCardReadyMs(): number {
  return staggerDelayMs(FORGE_MOCK_HERO_INDEX) + WELCOME_DURATION_MS;
}

export function forgeMockItemDelayMs(index: number): number {
  return index * FORGE_MOCK_ITEM_STAGGER_MS;
}

export function forgeMockNodeDelayMs(index: number): number {
  return forgeMockCardReadyMs() + forgeMockItemDelayMs(index);
}

export function forgeMockNodesPhaseEndMs(): number {
  const lastIndex = FORGE_MOCK_NODE_COUNT - 1;
  return forgeMockNodeDelayMs(lastIndex) + FORGE_MOCK_ITEM_DURATION_MS;
}

export function forgeMockFocusDelayMs(): number {
  return forgeMockNodesPhaseEndMs() + FORGE_MOCK_PAUSE_BEFORE_FOCUS_MS;
}

export function forgeMockStepsPhaseStartMs(): number {
  return (
    forgeMockFocusDelayMs() +
    FORGE_MOCK_FOCUS_DURATION_MS +
    FORGE_MOCK_PAUSE_BEFORE_STEPS_MS
  );
}

export function forgeMockStepDelayMs(index: number): number {
  return forgeMockStepsPhaseStartMs() + forgeMockItemDelayMs(index);
}

export function forgeMockNodeItemStyle(index: number): CSSProperties {
  return { animationDelay: `${forgeMockNodeDelayMs(index)}ms` };
}

export function forgeMockNodeDimStyle(): CSSProperties {
  return { animationDelay: `${forgeMockFocusDelayMs()}ms` };
}

export function forgeMockNodeFocusPillStyle(): CSSProperties {
  return { animationDelay: `${forgeMockFocusDelayMs()}ms` };
}

export function forgeMockStepItemStyle(index: number): CSSProperties {
  return { animationDelay: `${forgeMockStepDelayMs(index)}ms` };
}

export function forgeMockRootStyle(): CSSProperties {
  return {
    "--forge-mock-duration": `${FORGE_MOCK_ITEM_DURATION_MS}ms`,
    "--forge-mock-focus-duration": `${FORGE_MOCK_FOCUS_DURATION_MS}ms`,
    "--forge-mock-translate": `${FORGE_MOCK_TRANSLATE_PX}px`,
  } as CSSProperties;
}
