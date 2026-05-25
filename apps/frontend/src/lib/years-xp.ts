import type { YearsXpRange } from "@/types/contracts";

/** PT-BR labels — mirror backend YearsXpRange buckets. */
export const YEARS_XP_LABELS: Record<YearsXpRange, string> = {
  "0-1": "0–1 ano",
  "1-3": "1–3 anos",
  "3-5": "3–5 anos",
  "5+": "5+ anos",
};

export const YEARS_XP_OPTIONS: Array<{ value: YearsXpRange; label: string }> = (
  Object.entries(YEARS_XP_LABELS) as Array<[YearsXpRange, string]>
).map(([value, label]) => ({ value, label }));

export function formatYearsXpLabel(value: YearsXpRange): string {
  return YEARS_XP_LABELS[value];
}
