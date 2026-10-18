import { describe, expect, it } from "vitest";

import { apiPrefixRewrites } from "./api-proxy-rewrites.mjs";

describe("apiPrefixRewrites", () => {
  it("sends billing calls, including the Stripe webhook, to the backend", () => {
    const rewrites = apiPrefixRewrites("http://backend:8000/");

    expect(rewrites).toEqual(
      expect.arrayContaining([
        {
          source: "/billing",
          destination: "http://backend:8000/billing",
        },
        {
          source: "/billing/:path*",
          destination: "http://backend:8000/billing/:path*",
        },
      ]),
    );
  });
});
