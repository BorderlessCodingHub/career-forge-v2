import type { Metadata } from "next";

import { WelcomeLanding } from "@/components/marketing/WelcomeLanding";

export const metadata: Metadata = {
  title: "Welcome · Career Forge",
  description:
    "A roadmap that only moves when you prove it. Career Forge for Borderless BASE & PSP — live forge, mastery gated.",
};

export default function WelcomePage() {
  return <WelcomeLanding />;
}
