/** Static illustration data for `/welcome/plg` — not a live forge run. */

export const FORGE_MOCK_STEPS = [
  { n: "01", label: "Diagnosing profile", state: "done" },
  { n: "02", label: "Planning coverage", state: "done" },
  { n: "03", label: "Forging roadmap", state: "live" },
  { n: "04", label: "Ready to validate", state: "queued" },
] as const;

export const FORGE_MOCK_NODES = [
  { title: "RAG retrieval", status: "aprovado" },
  { title: "Agent tools", status: "validar" },
  { title: "Evals harness", status: "em_estudo" },
  { title: "Fine tuning", status: "bloqueado" },
] as const;

/** Marketing “you are here” focus — not a user picker. */
export const FORGE_MOCK_FOCUS_NODE_INDEX = 1;
