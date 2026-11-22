// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import { ArtifactShell } from "@/components/layout/ArtifactShell";
import { SetupHeader } from "@/components/layout/SetupHeader";
import { Navbar } from "@/components/marketing/welcome/Navbar";
import { WelcomeShell } from "@/components/marketing/welcome/WelcomeShell";

const navigation = vi.hoisted(() => ({
  pathname: "/onboarding",
}));

vi.mock("next/navigation", () => ({
  usePathname: () => navigation.pathname,
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("next/link", () => ({
  default: ({ children, href, ...rest }: { children: ReactNode; href: string }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/user-session", () => ({
  hasEmailIdentity: () => true,
  signOut: vi.fn(),
}));

vi.mock("@/lib/api-client", () => ({
  getMyProfile: vi.fn(async () => ({ email: "ana@example.com" })),
  updateMyLocale: vi.fn(),
}));

function renderWithLocale(node: ReactNode) {
  return render(<NextIntlClientProvider locale="en">{node}</NextIntlClientProvider>);
}

afterEach(() => {
  cleanup();
  navigation.pathname = "/onboarding";
});

describe("Fundamentals entry", () => {
  it("links from the signed-in setup and artifact bars, and Welcome does not", async () => {
    navigation.pathname = "/onboarding";
    renderWithLocale(<SetupHeader />);
    const setup = await screen.findByTestId("fundamentals-link");
    expect(setup.getAttribute("href")).toBe("/fundamentals/rag-engineer");
    expect(screen.getByTestId("setup-topbar").contains(setup)).toBe(true);
    cleanup();

    navigation.pathname = "/roadmap";
    renderWithLocale(<ArtifactShell>trail</ArtifactShell>);
    const artifact = await screen.findByTestId("fundamentals-link");
    expect(artifact.getAttribute("href")).toBe("/fundamentals/rag-engineer");
    expect(screen.getByTestId("artifact-topbar").contains(artifact)).toBe(true);
    cleanup();

    renderWithLocale(<Navbar />);
    expect(screen.queryByTestId("fundamentals-link")).toBeNull();
    expect(document.querySelector('a[href^="/fundamentals"]')).toBeNull();
    cleanup();

    renderWithLocale(<WelcomeShell />);
    expect(screen.queryByTestId("fundamentals-link")).toBeNull();
    expect(document.querySelector('a[href^="/fundamentals"]')).toBeNull();
  });
});
