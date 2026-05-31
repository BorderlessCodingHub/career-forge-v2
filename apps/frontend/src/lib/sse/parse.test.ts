import { describe, expect, it } from "vitest";

import { parseSseBlock } from "@/lib/sse/parse";

describe("parseSseBlock", () => {
  it("reads event and data lines", () => {
    const block = 'event: mapping_dimension\ndata: {"type":"mapping_dimension","index":0}';
    expect(parseSseBlock(block)).toEqual({
      event: "mapping_dimension",
      data: '{"type":"mapping_dimension","index":0}',
    });
  });

  it("defaults event name to message", () => {
    const block = 'data: {"type":"graph_complete"}';
    expect(parseSseBlock(block)?.event).toBe("message");
  });
});
