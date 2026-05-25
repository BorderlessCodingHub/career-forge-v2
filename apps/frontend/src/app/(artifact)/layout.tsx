import type { ReactNode } from "react";

import { ArtifactShellLayout } from "@/components/layout/ArtifactShellLayout";

export default function ArtifactLayout({ children }: { children: ReactNode }) {
  return <ArtifactShellLayout>{children}</ArtifactShellLayout>;
}
