// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api-client", () => ({
  startBillingCheckout: vi.fn(),
}));

import { PaywallPanel } from "./PaywallPanel";

afterEach(cleanup);

describe("PaywallPanel", () => {
  it("names USD $7/mo after the included forge is spent", () => {
    render(<PaywallPanel checkoutAvailable />);

    const panel = screen.getByTestId("paywall-panel");
    expect(panel.textContent).toContain("USD $7/mo");
    expect(panel.textContent?.toLowerCase()).not.toContain("free forge used");
    expect(panel.textContent?.toLowerCase()).not.toContain("subscribe to continue");
    expect(panel.textContent?.toLowerCase()).not.toContain("start diagnosis");
    expect(panel.textContent).not.toMatch(/R\$|BRL/);
    expect(screen.queryByText(/checkout is not live/i)).toBeNull();
  });
});
