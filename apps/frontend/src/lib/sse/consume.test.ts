import { afterEach, describe, expect, it, vi } from "vitest";

import { PAYWALL_COPY } from "@/lib/paywall";
import { QUOTA_EXHAUSTED_COPY } from "@/lib/quota";
import { consumeFetchEventStream } from "@/lib/sse/consume";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("consumeFetchEventStream", () => {
  it("throws PaywallError on HTTP 402", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: {
              code: "paywall",
              message: PAYWALL_COPY,
              checkout_available: false,
            },
          }),
          {
            status: 402,
            statusText: "Payment Required",
            headers: { "Content-Type": "application/json" },
          },
        ),
      ),
    );

    await expect(
      consumeFetchEventStream(
        "https://api.example/diagnosis/interview/start/stream",
        { method: "POST" },
        () => undefined,
        () => null,
      ),
    ).rejects.toMatchObject({
      name: "PaywallError",
      message: PAYWALL_COPY,
      checkoutAvailable: false,
    });
  });

  it("still maps quota copy on exhausted SSE errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "experimental quota exhausted — come back later",
          }),
          {
            status: 429,
            statusText: "Too Many Requests",
            headers: { "Content-Type": "application/json" },
          },
        ),
      ),
    );

    await expect(
      consumeFetchEventStream(
        "https://api.example/forge/stream",
        { method: "POST" },
        () => undefined,
        () => null,
      ),
    ).rejects.toThrow(QUOTA_EXHAUSTED_COPY);
  });
});
