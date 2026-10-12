// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import ForgePage from "./page";

const api = vi.hoisted(() => ({
  startForgeRunFromProfile: vi.fn(),
  streamForgeRun: vi.fn(),
  syncBillingSession: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn() }),
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

const providerDump =
  "Error code: 402 - {'error': {'message': 'This request requires more credits', " +
  "'user_id': 'user_example', " +
  "'url': 'https://openrouter.ai/workspaces/default/keys/" +
  "e".repeat(64) +
  "'}}";

afterEach(() => {
  cleanup();
  api.startForgeRunFromProfile.mockReset();
  api.streamForgeRun.mockReset();
});

describe("Forge page", () => {
  it("shows the retry sentence instead of a provider dump", async () => {
    api.startForgeRunFromProfile.mockResolvedValue({ run_id: "run-1" });
    api.streamForgeRun.mockImplementation(async (_runId: string, effects: { onError?: (message: string) => void }) => {
      effects.onError?.(providerDump);
      return [];
    });

    render(<ForgePage />);

    expect(
      await screen.findByText(
        "We couldn't finish your trail just now. Try again in a few minutes.",
      ),
    ).toBeTruthy();
    expect(screen.getByRole("button", { name: "Try again" })).toBeTruthy();
    expect(screen.queryByText(/openrouter/i)).toBeNull();
    expect(screen.queryByText(/Error code/i)).toBeNull();
    expect(screen.queryByText(/user_id/i)).toBeNull();
  });
});
