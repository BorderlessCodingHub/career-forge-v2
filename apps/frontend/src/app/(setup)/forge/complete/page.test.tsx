// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import ForgeCompletePage from "./page";

const api = vi.hoisted(() => ({
  getRoadmap: vi.fn(),
  listForges: vi.fn(),
  mintResumeLink: vi.fn(),
  emailResumeLink: vi.fn(),
  absoluteAppUrl: (path: string) => path,
}));

vi.mock("next/link", () => ({
  default: ({ children, href, ...rest }: { children: ReactNode; href: string }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("@/components/auth", () => ({
  ProductEntryGate: ({ children }: { children: ReactNode }) => children,
}));

vi.mock("@/lib/api-client", () => api);

afterEach(() => {
  cleanup();
  sessionStorage.clear();
  api.getRoadmap.mockReset();
  api.listForges.mockReset();
});

describe("Forge complete", () => {
  it("does not store a session graph when hydrating the reveal from the server", async () => {
    sessionStorage.removeItem("career-forge.forge-graph");
    api.getRoadmap.mockResolvedValue({
      nodes: [
        {
          node_id: "agent-tool-use",
          title: "Tool use",
          status: "recomendado",
          mastery_score: 10,
          priority: "high",
          rationale: "start here",
          prerequisites: [],
        },
      ],
    });
    api.listForges.mockResolvedValue({ items: [] });

    render(<ForgeCompletePage />);

    expect(await screen.findByText(/Tool use/)).toBeTruthy();
    expect(sessionStorage.getItem("career-forge.forge-graph")).toBeNull();
  });
});
