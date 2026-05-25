import type { HTMLAttributes } from "react";

export function Drawer({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <aside
      className={`fixed right-0 top-0 h-full w-96 border-l border-border bg-surface-elevated p-6 ${className}`}
      {...props}
    />
  );
}
