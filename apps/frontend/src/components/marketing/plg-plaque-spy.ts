/** Sticky split-flap plaque on `/welcome/plg` — visual only; not product chrome. */

export const PLG_PLAQUE_LABELS = [
  "Built for Borderless · BASE & PSP learners",
  "Career Forge helps you before, during, and after the forge.",
  "Works the way the product works",
] as const;

export const PLG_PLAQUE_SECTION_IDS = [
  "plg-section-phases",
  "plg-section-features",
] as const;

/** Full flip (out + in). Grill: ~520ms split-flap. */
export const PLG_PLAQUE_FLIP_MS = 520;

export const PLG_PLAQUE_FLIP_HALF_MS = PLG_PLAQUE_FLIP_MS / 2;

/**
 * Scroll-spy: last section whose top has crossed above the plaque bottom.
 * Index 0 is the rest label (audience) before any section crosses.
 */
export function plgPlaqueLabelIndex(
  plaqueBottom: number,
  sectionTops: readonly number[],
): number {
  let index = 0;
  for (let i = 0; i < sectionTops.length; i++) {
    const top = sectionTops[i];
    if (top !== undefined && top < plaqueBottom) {
      index = i + 1;
    }
  }
  return index;
}
