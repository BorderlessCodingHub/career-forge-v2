// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { RoadmapNode } from "@/types/contracts";

import { NodeDrawer } from "./NodeDrawer";

vi.mock("@/lib/api-client", () => ({
  getKnowledgeGaps: vi.fn().mockResolvedValue([]),
}));

afterEach(cleanup);

const node: RoadmapNode = {
  node_id: "http-basics",
  title: "HTTP basics",
  category: "foundations",
  description: "",
  icon: "code",
  side: "left",
  sort_order: 1,
  prerequisites: [],
  outcomes: [],
  rubric: [],
  status: "em_estudo",
  mastery_score: 20,
  tasks: [],
  references: [
    {
      id: "mdn-http",
      title: "MDN HTTP",
      url: "https://developer.mozilla.org/en-US/docs/Web/HTTP",
      done: false,
    },
  ],
  checklist_completed: 0,
  checklist_total: 1,
};

describe("NodeDrawer References", () => {
  it("opens a Reference through its in-product Node + item address", () => {
    render(
      <NodeDrawer
        node={node}
        onClose={() => undefined}
        onOpenMentor={() => undefined}
      />,
    );

    const link = screen.getByTestId("open-reference-mdn-http");
    expect(link.getAttribute("href")).toBe(
      "/reference?node=http-basics&item=mdn-http",
    );
    expect(link.getAttribute("target")).toBeNull();
  });
});
