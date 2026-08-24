import type { Metadata } from "next";

import { OperatorConsole } from "@/components/operator/OperatorConsole";

export const metadata: Metadata = {
  title: "Operator console · Career Forge",
  robots: {
    index: false,
    follow: false,
  },
};

export default function OperatorPage() {
  return <OperatorConsole />;
}
