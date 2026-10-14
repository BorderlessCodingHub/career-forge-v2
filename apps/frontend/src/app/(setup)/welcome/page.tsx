import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import { getTranslations } from "next-intl/server";

import { WelcomeShell } from "@/components/marketing/welcome/WelcomeShell";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-welcome-sans",
  display: "swap",
});

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("welcome.meta");
  return {
    title: t("title"),
    description: t("description"),
  };
}

export default function WelcomePage() {
  return (
    <WelcomeShell
      className={`${plusJakarta.variable} ${plusJakarta.className}`}
    />
  );
}
