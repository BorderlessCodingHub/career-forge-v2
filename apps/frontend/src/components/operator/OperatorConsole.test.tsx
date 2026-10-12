// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  getOperatorContentSkills,
  getOperatorCostPool,
  getOperatorEmbedHosts,
  getOperatorMe,
  getOperatorPilotEmails,
  getOperatorProviderSwitch,
  getOperatorSeats,
} from "@/lib/operator-console";

import { OperatorConsole } from "./OperatorConsole";

vi.mock("@/lib/operator-console", async () => {
  const actual = await vi.importActual<typeof import("@/lib/operator-console")>(
    "@/lib/operator-console",
  );
  return {
    ...actual,
    getOperatorMe: vi.fn(),
    getOperatorSeats: vi.fn(),
    getOperatorCostPool: vi.fn(),
    getOperatorPilotEmails: vi.fn(),
    getOperatorProviderSwitch: vi.fn(),
    getOperatorContentSkills: vi.fn(),
    getOperatorEmbedHosts: vi.fn(),
  };
});

beforeEach(() => {
  vi.mocked(getOperatorSeats).mockResolvedValue([]);
  vi.mocked(getOperatorCostPool).mockResolvedValue({
    year_month: "2026-10",
    estimated_cost_brl: 0,
    budget_brl: 500,
    billable_runs: 0,
    forge_runs: 0,
  });
  vi.mocked(getOperatorPilotEmails).mockResolvedValue([]);
  vi.mocked(getOperatorProviderSwitch).mockResolvedValue({
    on: false,
    run_provider: "direct",
    operator_email: null,
    written_at: null,
  });
  vi.mocked(getOperatorContentSkills).mockResolvedValue([]);
  vi.mocked(getOperatorEmbedHosts).mockResolvedValue({ pending: [], liberated: [] });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Operator console Provider switch", () => {
  it("does not give an editor the Provider switch", async () => {
    vi.mocked(getOperatorMe).mockResolvedValue({
      email: "editor@borderless.com",
      operator_id: 2,
      desk_roles: "editor",
      desks: ["content"],
    });

    render(<OperatorConsole />);

    expect(await screen.findByTestId("operator-tab-content")).toBeTruthy();
    expect(screen.queryByTestId("operator-tab-access")).toBeNull();
    expect(screen.queryByTestId("operator-provider-switch")).toBeNull();
    expect(screen.queryByTestId("operator-provider-switch-arm")).toBeNull();
  });

  it("gives an Access operator the Provider switch", async () => {
    vi.mocked(getOperatorMe).mockResolvedValue({
      email: "access@borderless.com",
      operator_id: 1,
      desk_roles: "access",
      desks: ["access"],
    });

    render(<OperatorConsole />);

    expect(await screen.findByTestId("operator-provider-switch-arm")).toBeTruthy();
    expect(screen.queryByTestId("operator-tab-content")).toBeNull();
  });

  it("gives an operator who holds both desks the Provider switch", async () => {
    vi.mocked(getOperatorMe).mockResolvedValue({
      email: "both@borderless.com",
      operator_id: 3,
      desk_roles: "both",
      desks: ["access", "content"],
    });

    render(<OperatorConsole />);

    expect(await screen.findByTestId("operator-provider-switch-arm")).toBeTruthy();
    expect(screen.getByTestId("operator-provider-switch-choice").textContent).toBe(
      "Direct provider",
    );
    expect(screen.getByTestId("operator-tab-access")).toBeTruthy();
    expect(screen.getByTestId("operator-tab-content")).toBeTruthy();
  });
});
