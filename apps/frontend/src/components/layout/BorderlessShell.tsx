/** Borderless chrome-less shell stub — HAC-23 theming reference. */
import type { HTMLAttributes } from "react";

export function BorderlessShell({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`min-h-screen bg-bg grid-dots ${className}`} {...props} />;
}
