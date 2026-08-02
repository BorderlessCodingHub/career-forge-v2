import {
  PROFILE_DIMENSION_KEYS,
  type RubricDimensionKey,
  type RubricMapItem,
} from "@/types/contracts";

/** Profile sidebar skeleton — labels/descriptions sync with backend PROFILE_DIMENSION_* */
const PROFILE_DIMENSIONS: Array<{
  rubric_key: RubricDimensionKey;
  label: string;
  description: string;
}> = [
  {
    rubric_key: "motivation_goal",
    label: "Goal",
    description: "Why this path and alignment with your goal",
  },
  {
    rubric_key: "background_transfer",
    label: "Where you come from",
    description: "Prior domain and habits you bring into tech",
  },
  {
    rubric_key: "learning_velocity",
    label: "Learning cadence",
    description: "How much you practice, how often, and how consistently",
  },
  {
    rubric_key: "hands_on_proof",
    label: "Hands-on proof",
    description: "Largest thing you have built, attempted, or shipped",
  },
  {
    rubric_key: "constraints",
    label: "Real context",
    description: "Hours/week, language, budget, how you study today",
  },
];

if (PROFILE_DIMENSIONS.length !== PROFILE_DIMENSION_KEYS.length) {
  throw new Error("PROFILE_DIMENSIONS out of sync with PROFILE_DIMENSION_KEYS");
}

export function buildSkeletonMappingProgress(): RubricMapItem[] {
  return PROFILE_DIMENSIONS.map((dim) => ({
    rubric_key: dim.rubric_key,
    label: dim.label,
    description: dim.description,
    confidence: 0,
    saturated: false,
    status: "pending" as const,
    note: "",
  }));
}

export function profileCompletenessPct(items: RubricMapItem[]): number {
  if (items.length === 0) return 0;
  const mapped = items.filter((item) => item.saturated || item.status === "mapped").length;
  return Math.round((mapped / items.length) * 100);
}
