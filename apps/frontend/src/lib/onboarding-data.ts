export type CareerGoal = {
  id: string;
  title: string;
  active: boolean;
};

export type DiagQuestion = {
  id: string;
  tag: string;
  prompt: string;
  placeholder: string;
};

export type DiagRound = {
  id: string;
  title: string;
  intro: string;
  maps: string[];
  questions: DiagQuestion[];
};

export const CAREER_GOALS: CareerGoal[] = [
  { id: "backend", title: "Backend Developer", active: true },
  { id: "data", title: "Data Engineer", active: false },
  { id: "frontend", title: "Frontend Developer", active: false },
];

export const DIAG_ROUNDS: DiagRound[] = [
  {
    id: "seniority",
    title: "Nível e contexto",
    intro: "Sem certo ou errado — quanto mais honesto, mais útil sua trilha.",
    maps: ["Senioridade", "Experiência prévia"],
    questions: [
      {
        id: "level",
        tag: "Senioridade",
        prompt: "Qual seu nível hoje com programação?",
        placeholder: "Ex.: estou começando, já sei JS básico, estudo há 6 meses…",
      },
      {
        id: "prior",
        tag: "Contexto",
        prompt: "Já estudou ou trabalhou com desenvolvimento antes?",
        placeholder: "Cursos, bootcamp, projetos pessoais, estágio…",
      },
    ],
  },
  {
    id: "stack",
    title: "Stack e domínios",
    intro: "Mapeamos familiaridade com conceitos que aparecem na trilha backend.",
    maps: ["Git", "Cliente/servidor"],
    questions: [
      {
        id: "git",
        tag: "Git",
        prompt: "Você já usou Git em algum projeto?",
        placeholder: "Clone, commit, push, branches…",
      },
      {
        id: "client_server",
        tag: "Domínio",
        prompt: "Consegue explicar a diferença entre frontend e backend?",
        placeholder: "Com suas palavras — o que cada um faz?",
      },
    ],
  },
  {
    id: "gaps",
    title: "Lacunas técnicas",
    intro: "Última rodada — HTTP, APIs e persistência.",
    maps: ["HTTP & APIs", "Banco de dados"],
    questions: [
      {
        id: "http",
        tag: "HTTP",
        prompt: "Você já fez alguma requisição HTTP ou chamou uma API?",
        placeholder: "GET, POST, status codes, JSON…",
      },
      {
        id: "db",
        tag: "DB",
        prompt: 'Ao pensar em "criar um usuário", o que vem primeiro — tela, banco ou requisição?',
        placeholder: "Descreva seu modelo mental…",
      },
    ],
  },
];

export const DIAG_MAP_LABELS = [
  "Senioridade",
  "Git",
  "HTTP & APIs",
  "Banco de dados",
] as const;
