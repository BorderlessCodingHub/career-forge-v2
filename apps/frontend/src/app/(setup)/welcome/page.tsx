import type { Metadata } from "next";

import { WelcomeLanding } from "@/components/marketing/WelcomeLanding";

export const metadata: Metadata = {
  title: "Welcome · Career Forge",
  description:
    "Borderless Career Forge — diagnose, forge a live skill trail, and validate mastery for BASE and PSP learners.",
};

export default function WelcomePage() {
  return <WelcomeLanding />;
}
