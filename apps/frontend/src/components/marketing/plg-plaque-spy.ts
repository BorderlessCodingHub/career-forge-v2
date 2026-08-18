/** Sticky split-flap plaque on `/welcome/plg` — visual only; not product chrome. */

export const PLG_PLAQUE_LABELS = [
  "Built for Borderless · BASE & PSP learners",
  "Career Forge helps you before, during, and after the forge.",
  "Works the way the product works",
] as const;

/** Stack step targets — one id per plaque label (trail → phases → features). */
export const PLG_PLAQUE_SECTION_IDS = [
  "plg-trail-product-mock-section",
  "plg-section-phases",
  "plg-section-features",
] as const;

/** Full flip (out + in). Grill: ~520ms split-flap. */
export const PLG_PLAQUE_FLIP_MS = 520;

export const PLG_PLAQUE_FLIP_HALF_MS = PLG_PLAQUE_FLIP_MS / 2;

/**
 * Stack scroll-spy: index of the topmost step whose wrapper top has crossed the
 * anchor (plaque bottom). Defaults to 0 before the first step crosses.
 */
export function plgPlaqueLabelIndex(
  anchorY: number,
  stepTops: readonly number[],
): number {
  let index = 0;
  for (let i = 0; i < stepTops.length; i++) {
    const top = stepTops[i];
    if (top !== undefined && top <= anchorY) {
      index = i;
    }
  }
  return index;
}
