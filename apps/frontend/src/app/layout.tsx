import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrains.variable} font-sans pb-8`}>
        {children}
        <DeployBadge />
      </body>
    </html>
  );
}
