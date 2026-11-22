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
  listForges: vi.fn(async () => ({
    items: [
      {
        public_id: "forge-fine-tuning",
        goal_id: "fine-tuning",
        title: "Roadmap · fine-tuning",
        is_active: true,
        created_at: "2026-11-22T00:00:00Z",
        graph_run_id: "run-fine-tuning",
      },
    ],
  })),
  listFundamentals: vi.fn(async () => ({
    goals: [{ goal_id: "rag-engineer" }, { goal_id: "agent-engineer" }],
  })),
}));

function renderWithLocale(node: ReactNode) {
  return render(<NextIntlClientProvider locale="en">{node}</NextIntlClientProvider>);
}

afterEach(() => {
  cleanup();
  navigation.pathname = "/onboarding";
});

describe("Fundamentals entry", () => {
  it("opens the Roadmap's Goal from a Roadmap and the first published guide elsewhere", async () => {
    navigation.pathname = "/roadmap";
    renderWithLocale(<ArtifactShell>trail</ArtifactShell>);
    const roadmap = await screen.findByTestId("fundamentals-link");
    expect(roadmap.getAttribute("href")).toBe("/fundamentals/fine-tuning");
    expect(screen.getByTestId("artifact-topbar").contains(roadmap)).toBe(true);
    cleanup();

    navigation.pathname = "/forges";
    renderWithLocale(<SetupHeader />);
    const forges = await screen.findByTestId("fundamentals-link");
    expect(forges.getAttribute("href")).toBe("/fundamentals/rag-engineer");
    expect(screen.getByTestId("setup-topbar").contains(forges)).toBe(true);
    cleanup();

    navigation.pathname = "/onboarding";
    renderWithLocale(<SetupHeader />);
    const setup = await screen.findByTestId("fundamentals-link");
    expect(setup.getAttribute("href")).toBe("/fundamentals/rag-engineer");
    cleanup();

    navigation.pathname = "/validate";
    renderWithLocale(<ArtifactShell>check</ArtifactShell>);
    const validate = await screen.findByTestId("fundamentals-link");
    expect(validate.getAttribute("href")).toBe("/fundamentals/rag-engineer");
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
