import {
  CTRR_DIMENSION_KEYS,
  type RubricDimensionKey,
  type RubricMapItem,
} from "@/types/contracts";

/** CTRR sidebar skeleton — labels/descriptions sync with backend CTRR_DIMENSION_* */
export const CTRR_DIMENSIONS: Array<{
  rubric_key: RubricDimensionKey;
  label: string;
  description: string;
}> = [
  {
    rubric_key: "learning_stage",
    label: "Senioridade",
    description: "Quanto você já praticou programação (cursos, exercícios, tempo)",
  },
  {
    rubric_key: "project_scope",
    label: "Escala",
    description: "Maior projeto que já construiu ou tentou construir",
  },
  {
    rubric_key: "background_context",
    label: "Contexto",
    description: "De onde você vem e como estuda tecnologia hoje",
  },
  {
    rubric_key: "hands_on_evidence",
    label: "Experiência prática",
    description: "Algo concreto que já fez ou tentou na prática",
  },
  {
    rubric_key: "git",
    label: "Git",
    description: "Se já usou Git ou GitHub em algum projeto",
  },
  {
    rubric_key: "client_server",
    label: "Cliente/servidor",
    description: "Como você entende frontend vs backend",
  },
  {
    rubric_key: "http_apis",
    label: "HTTP & APIs",
    description: "Se já viu ou fez requisições HTTP ou chamadas de API",
  },
  {
    rubric_key: "database",
    label: "Banco de dados",
    description: "Exposição a banco de dados ou SQL",
  },
];

if (CTRR_DIMENSIONS.length !== CTRR_DIMENSION_KEYS.length) {
  throw new Error("CTRR_DIMENSIONS out of sync with CTRR_DIMENSION_KEYS");
}

export function buildSkeletonMappingProgress(): RubricMapItem[] {
  return CTRR_DIMENSIONS.map((dim) => ({
    rubric_key: dim.rubric_key,
    label: dim.label,
    description: dim.description,
    confidence: 0,
    saturated: false,
  }));
}
