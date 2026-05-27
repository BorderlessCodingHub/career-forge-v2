import type { ButtonHTMLAttributes } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  const base =
    variant === "primary"
      ? "bg-accent text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-45 disabled:hover:opacity-45"
      : "border border-border bg-surface text-text-secondary disabled:cursor-not-allowed disabled:opacity-45";
  return (
    <button
      className={`rounded-md px-4 py-2 text-sm font-medium transition ${base} ${className}`}
      {...props}
    />
  );
}
