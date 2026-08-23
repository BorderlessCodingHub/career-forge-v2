import type { ReactNode } from "react";

import { SetupHeader } from "@/components/layout/SetupHeader";

export default function SetupLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <SetupHeader />
      {children}
    </>
  );
}
