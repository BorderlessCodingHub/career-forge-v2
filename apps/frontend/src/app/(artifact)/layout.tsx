import type { ReactNode } from "react";

import { ArtifactShell } from "@/components/layout/ArtifactShell";

export default function ArtifactLayout({ children }: { children: ReactNode }) {
  return <ArtifactShell>{children}</ArtifactShell>;
}
