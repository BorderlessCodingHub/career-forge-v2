import { describe, expect, it } from "vitest";

import {
  PAYWALL_COPY,
  PaywallError,
  isPaywallError,
  paywallErrorFromResponse,
} from "./paywall";

describe("paywallErrorFromResponse", () => {
  it("returns PaywallError on 402 with checkout flag", () => {
    const err = paywallErrorFromResponse(402, {
      detail: {
        code: "paywall",
        message: PAYWALL_COPY,
        checkout_available: true,
      },
    });
    expect(err).toBeInstanceOf(PaywallError);
    expect(err?.checkoutAvailable).toBe(true);
    expect(err?.message).toBe(PAYWALL_COPY);
  });

  it("treats missing checkout_available as false", () => {
    const err = paywallErrorFromResponse(402, {
      detail: { code: "paywall", message: PAYWALL_COPY },
    });
    expect(err?.checkoutAvailable).toBe(false);
  });

  it("ignores non-402 statuses", () => {
    expect(
      paywallErrorFromResponse(429, { detail: { message: "quota" } }),
    ).toBeNull();
  });
});

describe("isPaywallError", () => {
  it("narrows PaywallError", () => {
    const err: unknown = new PaywallError(false);
    expect(isPaywallError(err)).toBe(true);
    expect(isPaywallError(new Error("nope"))).toBe(false);
  });
});
