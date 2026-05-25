export type CareerGoal = {
  id: string;
  title: string;
  active: boolean;
};

export const CAREER_GOALS: CareerGoal[] = [
  { id: "fullstack", title: "Fullstack Engineer", active: true },
  { id: "data", title: "Data Engineer", active: true },
  { id: "ai-ml", title: "AI & ML Engineer", active: true },
  { id: "web3", title: "Web3", active: true },
];
