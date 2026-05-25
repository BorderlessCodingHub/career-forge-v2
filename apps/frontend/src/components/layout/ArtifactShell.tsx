import type { HTMLAttributes } from "react";

export function ArtifactShell({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`flex min-h-screen bg-bg-sidebar ${className}`} {...props} />
  );
}
