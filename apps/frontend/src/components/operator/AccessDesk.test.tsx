// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  addOperatorPilotEmail,
  getOperatorCostPool,
  getOperatorLearnerAccess,
  getOperatorLearnerAccessAudit,
  getOperatorPilotEmails,
  getOperatorProviderSwitch,
  patchOperatorLearnerAccess,
  removeOperatorPilotEmail,
  writeOperatorProviderSwitch,
} from "@/lib/operator-console";

import { AccessDesk } from "./AccessDesk";

vi.mock("@/lib/operator-console", () => ({
  addOperatorPilotEmail: vi.fn(),
  getOperatorCostPool: vi.fn(),
  getOperatorLearnerAccess: vi.fn(),
  getOperatorLearnerAccessAudit: vi.fn(),
  getOperatorPilotEmails: vi.fn(),
  getOperatorProviderSwitch: vi.fn(),
  patchOperatorLearnerAccess: vi.fn(),
  removeOperatorPilotEmail: vi.fn(),
  writeOperatorProviderSwitch: vi.fn(),
}));

const pilot = {
  email: "pilot@example.com",
  created_at: "2026-08-25T12:00:00Z",
  created_by_operator_id: 7,
};

const unsetSwitch = {
  on: false,
  run_provider: "direct" as const,
  operator_email: null,
  written_at: null,
};

beforeEach(() => {
  vi.mocked(getOperatorCostPool).mockResolvedValue({
    year_month: "2026-08",
    estimated_cost_brl: 10,
    budget_brl: 500,
    billable_runs: 4,
    forge_runs: 1,
  });
  vi.mocked(getOperatorPilotEmails).mockResolvedValue([pilot]);
  vi.mocked(getOperatorLearnerAccessAudit).mockResolvedValue([]);
  vi.mocked(getOperatorProviderSwitch).mockResolvedValue(unsetSwitch);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("AccessDesk Provider switch", () => {
  it("shows the Direct provider and no writer when nothing is stored", async () => {
    render(<AccessDesk />);

    const choice = await screen.findByTestId("operator-provider-switch-choice");
    expect(choice.textContent).toBe("Direct provider");
    expect(screen.queryByTestId("operator-provider-switch-writer")).toBeNull();
    expect(screen.getByTestId("operator-provider-switch").querySelector("ol, ul")).toBeNull();
  });

  it("replaces the recorded writer after an arm and does not list earlier clicks", async () => {
    vi.mocked(getOperatorProviderSwitch).mockResolvedValue({
      on: false,
      run_provider: "direct",
      operator_email: "access@borderless.com",
      written_at: "2026-10-11T09:00:00Z",
    });
    vi.mocked(writeOperatorProviderSwitch).mockResolvedValue({
      on: true,
      run_provider: "gateway",
      operator_email: "both@borderless.com",
      written_at: "2026-10-12T14:30:00Z",
    });

    render(<AccessDesk />);

    expect((await screen.findByTestId("operator-provider-switch-writer")).textContent).toBe(
      "access@borderless.com · 11 Oct 2026, 09:00 UTC",
    );

    fireEvent.click(screen.getByTestId("operator-provider-switch-arm"));

    expect((await screen.findByTestId("operator-provider-switch-choice")).textContent).toBe(
      "Model gateway",
    );
    const writers = screen.getAllByTestId("operator-provider-switch-writer");
    expect(writers).toHaveLength(1);
    expect(writers[0]?.textContent).toBe("both@borderless.com · 12 Oct 2026, 14:30 UTC");
    expect(screen.queryByText(/access@borderless.com/)).toBeNull();
    expect(screen.getByTestId("operator-provider-switch").querySelector("ol, ul")).toBeNull();
    expect(writeOperatorProviderSwitch).toHaveBeenCalledWith(true);
  });

  it("disarms back to the Direct provider and keeps a single writer", async () => {
    vi.mocked(getOperatorProviderSwitch).mockResolvedValue({
      on: true,
      run_provider: "gateway",
      operator_email: "access@borderless.com",
      written_at: "2026-10-12T14:30:00Z",
    });
    vi.mocked(writeOperatorProviderSwitch).mockResolvedValue({
      on: false,
      run_provider: "direct",
      operator_email: "both@borderless.com",
      written_at: "2026-10-12T15:00:00Z",
    });

    render(<AccessDesk />);

    fireEvent.click(await screen.findByTestId("operator-provider-switch-disarm"));

    expect((await screen.findByTestId("operator-provider-switch-choice")).textContent).toBe(
      "Direct provider",
    );
    const writers = screen.getAllByTestId("operator-provider-switch-writer");
    expect(writers).toHaveLength(1);
    expect(writers[0]?.textContent).toBe("both@borderless.com · 12 Oct 2026, 15:00 UTC");
    expect(writeOperatorProviderSwitch).toHaveBeenCalledWith(false);
  });

  it("keeps the previous choice and shows why a refused arm failed", async () => {
    vi.mocked(writeOperatorProviderSwitch).mockRejectedValue(
      new Error(
        "The Model gateway is not configured. Set OPENROUTER_API_KEY before turning the Provider switch on.",
      ),
    );

    render(<AccessDesk />);

    expect((await screen.findByTestId("operator-provider-switch-choice")).textContent).toBe(
      "Direct provider",
    );
    fireEvent.click(screen.getByTestId("operator-provider-switch-arm"));

    expect((await screen.findByTestId("operator-provider-switch-error")).textContent).toBe(
      "The Model gateway is not configured. Set OPENROUTER_API_KEY before turning the Provider switch on.",
    );
    expect(screen.getByTestId("operator-provider-switch-choice").textContent).toBe(
      "Direct provider",
    );
    expect(screen.queryByTestId("operator-provider-switch-writer")).toBeNull();
  });

  it("keeps the recorded writer and shows why a refused disarm failed", async () => {
    vi.mocked(getOperatorProviderSwitch).mockResolvedValue({
      on: true,
      run_provider: "gateway",
      operator_email: "access@borderless.com",
      written_at: "2026-10-12T14:30:00Z",
    });
    vi.mocked(writeOperatorProviderSwitch).mockRejectedValue(
      new Error(
        "The Direct provider is not configured. Set OPENAI_API_KEY before turning the Provider switch off.",
      ),
    );

    render(<AccessDesk />);

    fireEvent.click(await screen.findByTestId("operator-provider-switch-disarm"));

    expect((await screen.findByTestId("operator-provider-switch-error")).textContent).toBe(
      "The Direct provider is not configured. Set OPENAI_API_KEY before turning the Provider switch off.",
    );
    expect(screen.getByTestId("operator-provider-switch-choice").textContent).toBe("Model gateway");
    expect(screen.getByTestId("operator-provider-switch-writer").textContent).toBe(
      "access@borderless.com · 12 Oct 2026, 14:30 UTC",
    );
    expect(writeOperatorProviderSwitch).toHaveBeenCalledWith(false);
  });

  it("shows why the Provider switch could not be loaded", async () => {
    vi.mocked(getOperatorProviderSwitch).mockRejectedValue(
      new Error("Operator session required."),
    );

    render(<AccessDesk />);

    expect((await screen.findByTestId("operator-provider-switch-error")).textContent).toBe(
      "Operator session required.",
    );
    expect(screen.queryByTestId("operator-provider-switch-arm")).toBeNull();
  });
});

describe("AccessDesk pilot list", () => {
  it("lists, adds, and removes pilot emails without changing billing_entitled", async () => {
    vi.mocked(addOperatorPilotEmail).mockResolvedValue({
      email: "new@example.com",
      created_at: "2026-08-25T13:00:00Z",
      created_by_operator_id: 7,
    });
    vi.mocked(removeOperatorPilotEmail).mockResolvedValue();

    render(<AccessDesk />);

    expect(await screen.findByTestId("operator-pilot-email-pilot@example.com")).toBeTruthy();
    const listBadge = screen.getByTestId("operator-pilot-badge-pilot@example.com");
    expect(listBadge.textContent).toBe("pilot list");
    expect(listBadge.className).not.toContain("uppercase");

    fireEvent.change(screen.getByTestId("operator-pilot-email-input"), {
      target: { value: " New@Example.com " },
    });
    fireEvent.click(screen.getByTestId("operator-pilot-email-add"));

    expect(await screen.findByTestId("operator-pilot-email-new@example.com")).toBeTruthy();
    expect(addOperatorPilotEmail).toHaveBeenCalledWith("New@Example.com");

    fireEvent.click(screen.getByTestId("operator-pilot-email-remove-new@example.com"));

    await waitFor(() =>
      expect(screen.queryByTestId("operator-pilot-email-new@example.com")).toBeNull(),
    );
    expect(removeOperatorPilotEmail).toHaveBeenCalledWith("new@example.com");
    expect(patchOperatorLearnerAccess).not.toHaveBeenCalled();
  });

  it("shows the pilot list badge on a listed learner card", async () => {
    vi.mocked(getOperatorLearnerAccess).mockResolvedValue({
      email: pilot.email,
      operator_membership_label: null,
      membership_label: "external",
      membership_entitled: false,
      billing_entitled: false,
      pilot_email_listed: true,
      stripe_subscription_status: null,
      stripe_billing_locked: false,
    });

    render(<AccessDesk />);

    fireEvent.change(screen.getByTestId("operator-learner-email"), {
      target: { value: pilot.email },
    });
    fireEvent.click(screen.getByTestId("operator-learner-lookup"));

    expect((await screen.findByTestId("operator-access-pilot-badge")).textContent).toBe("pilot list");
    expect(screen.getByTestId("operator-access-card").textContent).toContain("Entitled");
  });
});
