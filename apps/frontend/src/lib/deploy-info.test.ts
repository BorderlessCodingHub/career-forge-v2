import { describe, expect, it } from "vitest";

import {
  formatBuildTime,
  getDeployBadgeLabel,
  shortBuildSha,
} from "@/lib/deploy-info";

describe("deploy-info", () => {
  it("shortBuildSha returns first 7 chars", () => {
    expect(shortBuildSha("abcdef1234567890")).toBe("abcdef1");
  });

  it("getDeployBadgeLabel returns local dev without env", () => {
    const prev = process.env.NEXT_PUBLIC_BUILD_SHA;
    delete process.env.NEXT_PUBLIC_BUILD_SHA;
    expect(getDeployBadgeLabel()).toBe("local dev");
    if (prev) process.env.NEXT_PUBLIC_BUILD_SHA = prev;
  });

  it("formatBuildTime parses ISO timestamps", () => {
    const formatted = formatBuildTime("2026-05-27T17:00:00.000Z");
    expect(formatted.length).toBeGreaterThan(0);
  });
});
