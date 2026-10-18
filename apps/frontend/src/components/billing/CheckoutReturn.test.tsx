// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api-client", () => ({
  syncBillingSession: vi.fn(),
}));

import { syncBillingSession } from "@/lib/api-client";

import { CheckoutReturn } from "./CheckoutReturn";

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("CheckoutReturn", () => {
  it("thanks the learner after the purchase is synced and links to the forge list", async () => {
    vi.mocked(syncBillingSession).mockResolvedValue({ billing_entitled: true });

    render(<CheckoutReturn billing="success" sessionId="cs_test_1" />);

    expect(screen.queryByRole("link", { name: "See your forges" })).toBeNull();
    expect(await screen.findByText("Thank you for your purchase.")).toBeTruthy();
    expect(syncBillingSession).toHaveBeenCalledWith("cs_test_1");
    expect(screen.getByRole("link", { name: "See your forges" }).getAttribute("href")).toBe(
      "/forges",
    );
  });

  it("shows the sync error and does not offer the forge list", async () => {
    vi.mocked(syncBillingSession).mockRejectedValue(new Error("nope"));

    render(<CheckoutReturn billing="success" sessionId="cs_test_1" />);

    expect(await screen.findByText("The purchase could not be confirmed.")).toBeTruthy();
    expect(screen.queryByRole("link", { name: "See your forges" })).toBeNull();
  });

  it("says nothing was charged and does not sync a cancelled checkout", async () => {
    render(<CheckoutReturn billing="cancel" sessionId={null} />);

    expect(screen.getByText("Nothing was charged.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "See your forges" }).getAttribute("href")).toBe(
      "/forges",
    );
    await waitFor(() => {
      expect(syncBillingSession).not.toHaveBeenCalled();
    });
  });
});
