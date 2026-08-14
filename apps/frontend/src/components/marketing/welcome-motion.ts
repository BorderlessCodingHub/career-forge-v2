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
