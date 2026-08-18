import type { Metadata } from "next";

import { PlgLanding } from "@/components/marketing/PlgLanding";

export const metadata: Metadata = {
  title: "Welcome · Career Forge",
  description:
    "The adaptive roadmap for BASE & PSP — diagnosis, live forge, mastery checks. Without a static syllabus.",
};

export default function WelcomePlgPage() {
  return <PlgLanding />;
}
