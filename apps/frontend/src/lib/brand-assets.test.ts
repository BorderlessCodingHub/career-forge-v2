import { afterEach, describe, expect, it } from "vitest";

import { brandAssetPath, BRAND_FAVICON, BRAND_LOGO_SVG } from "./brand-assets";

describe("brandAssetPath", () => {
  afterEach(() => {
    delete process.env.NEXT_PUBLIC_BASE_PATH;
  });

  it("resolves under public/brand without basePath", () => {
    expect(brandAssetPath(BRAND_LOGO_SVG)).toBe("/brand/borderless-logo.svg");
    expect(brandAssetPath(BRAND_FAVICON)).toBe("/brand/favicon.ico");
  });

  it("prefixes NEXT_PUBLIC_BASE_PATH (Labs /career-forge)", () => {
    process.env.NEXT_PUBLIC_BASE_PATH = "/career-forge";
    expect(brandAssetPath(BRAND_LOGO_SVG)).toBe(
      "/career-forge/brand/borderless-logo.svg",
    );
  });

  it("strips trailing slash on basePath", () => {
    process.env.NEXT_PUBLIC_BASE_PATH = "/career-forge/";
    expect(brandAssetPath("/favicon.ico")).toBe("/career-forge/brand/favicon.ico");
  });
});
