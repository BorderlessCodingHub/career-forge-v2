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

const YEAR_MESSAGE_KEYS = {
  "0-1": "years0to1",
  "1-3": "years1to3",
  "3-5": "years3to5",
  "5+": "years5plus",
} as const;

export type YearMessageKey = (typeof YEAR_MESSAGE_KEYS)[keyof typeof YEAR_MESSAGE_KEYS];

export function yearMessageKey(years: string): YearMessageKey | null {
  if (years in YEAR_MESSAGE_KEYS) {
    return YEAR_MESSAGE_KEYS[years as keyof typeof YEAR_MESSAGE_KEYS];
  }
  return null;
}

export function formatYearsXpLabel(value: YearsXpRange): string {
  return YEARS_XP_LABELS[value];
}
