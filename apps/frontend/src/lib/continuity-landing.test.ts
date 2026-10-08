import { describe, expect, it } from "vitest";

import { continuityOpenNodeId } from "./continuity-landing";

const spine = [
  { node_id: "locked", status: "bloqueado" },
  { node_id: "passed", status: "aprovado" },
  { node_id: "retrieval", status: "em_estudo" },
];

describe("continuityOpenNodeId", () => {
  it("opens the named node when it is still next", () => {
    expect(continuityOpenNodeId(spine, "retrieval", true)).toBe("retrieval");
  });

  it("opens the roadmap when the named node is no longer next", () => {
    expect(continuityOpenNodeId(spine, "passed", true)).toBeNull();
    expect(continuityOpenNodeId(spine, "missing", true)).toBeNull();
  });

  it("keeps an ordinary roadmap deep link", () => {
    expect(continuityOpenNodeId(spine, "passed", false)).toBe("passed");
  });
});
