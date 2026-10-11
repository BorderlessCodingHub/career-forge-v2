// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("@/lib/api-client", () => ({
  listForges: vi.fn(),
  getMyProfile: vi.fn(),
  openForge: vi.fn(),
  startForgeRunFromProfile: vi.fn(),
}));

import { getMyProfile, listForges } from "@/lib/api-client";

import { LandingRecoveryGate } from "./LandingRecoveryGate";

afterEach(cleanup);

describe("LandingRecoveryGate", () => {
  it("reads the return-visit copy from the catalog", async () => {
    vi.mocked(listForges).mockResolvedValue({
      items: [
        {
          public_id: "forge-1",
          goal_id: "agent-engineer",
          title: "Roadmap · agent-engineer",
          is_active: true,
          created_at: "2026-10-10T00:00:00Z",
          graph_run_id: "run-1",
        },
      ],
    });
    vi.mocked(getMyProfile).mockResolvedValue({
      has_diagnosis: true,
    } as Awaited<ReturnType<typeof getMyProfile>>);

    render(<LandingRecoveryGate />);

    expect(await screen.findByRole("heading", { name: "Welcome back" })).toBeTruthy();
    await waitFor(() => {
      expect(
        screen.getByText(
          "You have 1 saved forge. Continue where you left off, browse all, or start a new one.",
        ),
      ).toBeTruthy();
    });
    expect(screen.getByText("Last forge")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Continue" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "View all" })).toBeTruthy();
    expect(
      screen.getByRole("button", { name: "Forge again from last diagnosis" }),
    ).toBeTruthy();
    expect(screen.getByRole("button", { name: "New forge" })).toBeTruthy();
  });
});
