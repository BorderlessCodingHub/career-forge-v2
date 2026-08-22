import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";

import { WelcomeShell } from "@/components/marketing/welcome/WelcomeShell";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-welcome-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Welcome · Career Forge",
  description:
    "A roadmap that only moves when you prove it. Career Forge for Borderless BASE & PSP — live forge, mastery gated.",
};

export default function WelcomePage() {
  return (
    <WelcomeShell
      className={`${plusJakarta.variable} ${plusJakarta.className}`}
    />
  );
}
