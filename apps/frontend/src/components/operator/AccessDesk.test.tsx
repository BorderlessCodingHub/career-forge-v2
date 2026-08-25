// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  addOperatorPilotEmail,
  getOperatorCostPool,
  getOperatorLearnerAccess,
  getOperatorLearnerAccessAudit,
  getOperatorPilotEmails,
  patchOperatorLearnerAccess,
  removeOperatorPilotEmail,
} from "@/lib/operator-console";

import { AccessDesk } from "./AccessDesk";

vi.mock("@/lib/operator-console", () => ({
  addOperatorPilotEmail: vi.fn(),
  getOperatorCostPool: vi.fn(),
  getOperatorLearnerAccess: vi.fn(),
  getOperatorLearnerAccessAudit: vi.fn(),
  getOperatorPilotEmails: vi.fn(),
  patchOperatorLearnerAccess: vi.fn(),
  removeOperatorPilotEmail: vi.fn(),
}));

const pilot = {
  email: "pilot@example.com",
  created_at: "2026-08-25T12:00:00Z",
  created_by_operator_id: 7,
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
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
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
