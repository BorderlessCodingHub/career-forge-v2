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
    label: "Objetivo",
    description: "Por que esse caminho e alinhamento com sua meta",
  },
  {
    rubric_key: "background_transfer",
    label: "De onde você vem",
    description: "Área anterior e hábitos que você traz para tech",
  },
  {
    rubric_key: "learning_velocity",
    label: "Ritmo de aprendizado",
    description: "Quanto pratica, com que frequência e consistência",
  },
  {
    rubric_key: "hands_on_proof",
    label: "Prova prática",
    description: "Maior coisa que construiu, tentou ou entregou",
  },
  {
    rubric_key: "constraints",
    label: "Contexto real",
    description: "Tempo/semana, idioma, budget, como estuda hoje",
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
