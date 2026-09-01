import { describe, expect, it } from "vitest";

import {
  QUOTA_EXHAUSTED_COPY,
  toUserFacingApiError,
} from "./quota";

describe("toUserFacingApiError", () => {
  it("maps quota 429 copy, not OTP rate-limit 429", () => {
    expect(
      toUserFacingApiError(
        429,
        "experimental quota exhausted — come back on day 1 of next month",
      ),
    ).toBe(QUOTA_EXHAUSTED_COPY);
    expect(
      toUserFacingApiError(429, "too many OTP requests — try again later"),
    ).toBe("too many OTP requests — try again later");
  });
});
