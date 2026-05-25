import type { HTMLAttributes } from "react";

type PillProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: "default" | "mint" | "warning";
};

export function Pill({ tone = "default", className = "", ...props }: PillProps) {
  const tones = {
    default: "bg-surface-elevated text-text-secondary border-border",
    mint: "bg-accent-mint/10 text-accent-mint border-accent-mint/30",
    warning: "bg-warning/10 text-warning border-warning/30",
  };
  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${tones[tone]} ${className}`}
      {...props}
    />
  );
}
