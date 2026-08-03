import type { YearsXpRange } from "@/types/contracts";

/** English labels — mirror backend YearsXpRange buckets. */
const YEARS_XP_LABELS: Record<YearsXpRange, string> = {
  "0-1": "0–1 year",
  "1-3": "1–3 years",
  "3-5": "3–5 years",
  "5+": "5+ years",
};

export const YEARS_XP_OPTIONS: Array<{ value: YearsXpRange; label: string }> = (
  Object.entries(YEARS_XP_LABELS) as Array<[YearsXpRange, string]>
).map(([value, label]) => ({ value, label }));

export function formatYearsXpLabel(value: YearsXpRange): string {
  return YEARS_XP_LABELS[value];
}
