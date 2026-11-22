import { describe, expect, it } from "vitest";

import { apiPrefixRewrites, fundamentalsJsonRewrites } from "./api-proxy-rewrites.mjs";

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

  it("does not send the Fundamentals page path to the API", () => {
    const sources = apiPrefixRewrites("http://backend:8000").map((rewrite) => rewrite.source);

    expect(sources).not.toContain("/fundamentals");
    expect(sources).not.toContain("/fundamentals/:path*");
  });
});

describe("fundamentalsJsonRewrites", () => {
  it("proxies the catalog and the guide, and leaves the page path alone", () => {
    expect(fundamentalsJsonRewrites("http://backend:8000/")).toEqual([
      {
        source: "/fundamentals",
        destination: "http://backend:8000/fundamentals",
      },
      {
        source: "/fundamentals/:goalId/guide",
        destination: "http://backend:8000/fundamentals/:goalId/guide",
      },
    ]);
  });
});
