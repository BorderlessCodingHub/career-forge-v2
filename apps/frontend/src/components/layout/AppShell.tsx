import type { HTMLAttributes } from "react";

export function AppShell({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`min-h-screen bg-bg ${className}`} {...props} />;
}
