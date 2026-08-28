import { afterEach, describe, expect, it } from "vitest";

import { learnAssetSrc } from "./learn-assets";

describe("learnAssetSrc", () => {
  afterEach(() => {
    delete process.env.NEXT_PUBLIC_BASE_PATH;
  });

  it("keeps the markdown src when there is no basePath", () => {
    expect(learnAssetSrc("/learn/rag-embeddings-tube-map.svg")).toBe(
      "/learn/rag-embeddings-tube-map.svg",
    );
  });

  it("prefixes NEXT_PUBLIC_BASE_PATH (Labs /career-forge)", () => {
    process.env.NEXT_PUBLIC_BASE_PATH = "/career-forge";
    expect(learnAssetSrc("/learn/rag-embeddings-tube-map.svg")).toBe(
      "/career-forge/learn/rag-embeddings-tube-map.svg",
    );
  });

  it("strips a trailing slash on basePath", () => {
    process.env.NEXT_PUBLIC_BASE_PATH = "/career-forge/";
    expect(learnAssetSrc("/learn/ok.svg")).toBe("/career-forge/learn/ok.svg");
  });

  it("does not prefix an src that already carries the basePath", () => {
    process.env.NEXT_PUBLIC_BASE_PATH = "/career-forge";
    expect(learnAssetSrc("/career-forge/learn/ok.svg")).toBe(
      "/career-forge/learn/ok.svg",
    );
  });
});
