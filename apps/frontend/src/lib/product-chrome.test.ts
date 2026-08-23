import { describe, expect, it } from "vitest";

import {
  isMarketingRoute,
  isResumeRoute,
  isShareRoute,
  shouldShowArtifactShell,
  shouldShowSetupHeader,
} from "./product-chrome";

describe("product chrome routes", () => {
  it("detects marketing routes", () => {
    expect(isMarketingRoute("/welcome")).toBe(true);
    expect(isMarketingRoute("/welcome/plg")).toBe(true);
    expect(isMarketingRoute("/")).toBe(false);
  });

  it("detects resume and share routes", () => {
    expect(isResumeRoute("/resume/abc123")).toBe(true);
    expect(isShareRoute("/share/abc123")).toBe(true);
    expect(isResumeRoute("/share/abc123")).toBe(false);
  });
});

describe("shouldShowSetupHeader", () => {
  it("shows on signed-in product routes", () => {
    expect(shouldShowSetupHeader("/", true)).toBe(true);
    expect(shouldShowSetupHeader("/forges", true)).toBe(true);
    expect(shouldShowSetupHeader("/onboarding", true)).toBe(true);
  });

  it("hides on marketing, resume, and when signed out", () => {
    expect(shouldShowSetupHeader("/welcome", true)).toBe(false);
    expect(shouldShowSetupHeader("/welcome/plg", true)).toBe(false);
    expect(shouldShowSetupHeader("/resume/token", true)).toBe(false);
    expect(shouldShowSetupHeader("/", false)).toBe(false);
  });
});

describe("shouldShowArtifactShell", () => {
  it("shows for signed-in artifact routes and public share", () => {
    expect(shouldShowArtifactShell("/roadmap", true)).toBe(true);
    expect(shouldShowArtifactShell("/share/token", false)).toBe(true);
  });

  it("hides when signed out on gated artifact routes", () => {
    expect(shouldShowArtifactShell("/roadmap", false)).toBe(false);
    expect(shouldShowArtifactShell("/validate", false)).toBe(false);
  });
});
