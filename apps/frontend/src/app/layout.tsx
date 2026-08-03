import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

import { DeployBadge } from "@/components/layout";
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
