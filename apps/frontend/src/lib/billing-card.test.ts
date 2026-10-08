import { describe, expect, it, vi } from "vitest";

import { redirectToCardUpdate } from "./billing-card";

describe("redirectToCardUpdate", () => {
  it("opens the portal session and does not touch the roadmap", async () => {
    const startPortal = vi.fn().mockResolvedValue("https://billing.stripe.com/p/session/fresh");
    const assign = vi.fn();

    await redirectToCardUpdate(startPortal, assign);

    expect(startPortal).toHaveBeenCalledOnce();
    expect(assign).toHaveBeenCalledWith("https://billing.stripe.com/p/session/fresh");
  });
});
