import type { ButtonHTMLAttributes } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  const base =
    variant === "primary"
      ? "bg-accent text-white hover:opacity-90"
      : "border border-border bg-surface text-text-secondary";
  return (
    <button
      className={`rounded-md px-4 py-2 text-sm font-medium transition ${base} ${className}`}
      {...props}
    />
  );
}
