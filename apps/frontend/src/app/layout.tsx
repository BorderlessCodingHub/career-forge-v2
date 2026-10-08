import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages } from "next-intl/server";

import { LocaleHydrator } from "@/components/i18n/LocaleHydrator";
import { DeployBadge } from "@/components/layout";
import { brandAssetPath, BRAND_FAVICON } from "@/lib/brand-assets";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Career Forge",
  description:
    "Adaptive skill graph — diagnose, forge a live trail, and validate mastery.",
  icons: {
    icon: [
      {
        url: brandAssetPath(BRAND_FAVICON),
        sizes: "32x32",
        type: "image/x-icon",
      },
    ],
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body className={`${inter.variable} ${jetbrains.variable} font-sans pb-8`}>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <LocaleHydrator />
          {children}
          <DeployBadge />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
