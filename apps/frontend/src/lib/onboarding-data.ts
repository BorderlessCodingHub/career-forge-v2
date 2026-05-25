export type CareerGoal = {
  id: string;
  title: string;
  active: boolean;
};

export const CAREER_GOALS: CareerGoal[] = [
  { id: "backend", title: "Backend Developer", active: true },
  { id: "data", title: "Data Engineer", active: false },
  { id: "frontend", title: "Frontend Developer", active: false },
];
