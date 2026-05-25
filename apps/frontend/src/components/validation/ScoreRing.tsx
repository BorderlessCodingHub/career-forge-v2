"use client";

type ScoreRingProps = {
  score: number;
  status: "aprovado" | "revisar";
};

export function ScoreRing({ score, status }: ScoreRingProps) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const stroke = status === "aprovado" ? "var(--success)" : "var(--warning)";

  return (
    <div className="relative inline-flex h-36 w-36 items-center justify-center" data-testid="validation-score">
      <svg className="-rotate-90" width="144" height="144" viewBox="0 0 144 144" aria-hidden>
        <circle cx="72" cy="72" r={radius} fill="none" stroke="var(--border)" strokeWidth="10" />
        <circle
          cx="72"
          cy="72"
          r={radius}
          fill="none"
          stroke={stroke}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="absolute text-center">
        <p className="text-3xl font-semibold text-text-primary">{score}</p>
        <p className="text-xs uppercase tracking-widest text-text-muted">/ 100</p>
      </div>
    </div>
  );
}
