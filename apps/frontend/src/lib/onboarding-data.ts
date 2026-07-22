type CareerGoal = {
  id: string;
  title: string;
  active: boolean;
};

export const CAREER_GOALS: CareerGoal[] = [
  { id: "rag-engineer", title: "Production RAG & Advanced Retrieval", active: true },
  { id: "agent-engineer", title: "Agent Engineering", active: true },
  { id: "llm-evals", title: "LLM Evaluation & Observability", active: true },
  { id: "fine-tuning", title: "Fine-Tuning & Alignment", active: true },
];
