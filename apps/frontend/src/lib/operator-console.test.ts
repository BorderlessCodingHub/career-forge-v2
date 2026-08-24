import { describe, expect, it } from "vitest";

import { operatorApiUrl, visibleOperatorDesks } from "./operator-console";

describe("operatorApiUrl", () => {
  it("keeps Operator cookie requests on the basePath origin", () => {
    process.env.NEXT_PUBLIC_BASE_PATH = "/career-forge";
    process.env.NEXT_PUBLIC_BACKEND_URL = "http://localhost:8000";

    expect(operatorApiUrl("/operator/me")).toBe("/career-forge/operator/me");
  });
});

describe("visibleOperatorDesks", () => {
  it("shows both desk rooms in their canonical order", () => {
    expect(visibleOperatorDesks(["content", "access"])).toEqual([
      { id: "access", label: "Access" },
      { id: "content", label: "Content" },
    ]);
  });

  it("hides desks outside the operator grant", () => {
    expect(visibleOperatorDesks(["content"])).toEqual([
      { id: "content", label: "Content" },
    ]);
    expect(visibleOperatorDesks(["access"])).toEqual([
      { id: "access", label: "Access" },
    ]);
  });
});
