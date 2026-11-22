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

  it("does not offer the skill lesson", () => {
    render(
      <NodeDrawer
        node={{
          ...node,
          canonical: { skill_id: "http-basics", title: "HTTP deep-dive" },
        }}
        onClose={() => undefined}
        onOpenMentor={() => undefined}
      />,
    );

    expect(screen.queryByTestId("canonical-skill-content")).toBeNull();
    expect(screen.queryByTestId("open-canonical-learn")).toBeNull();
    expect(screen.queryByRole("link", { name: "HTTP deep-dive" })).toBeNull();
    expect(screen.queryByText("HTTP deep-dive")).toBeNull();

    const validate = screen.getByTestId("validate-node-cta");
    expect(validate.closest("a")?.getAttribute("href")).toBe(
      "/validate?node=http-basics&mode=loop",
    );
  });
});
