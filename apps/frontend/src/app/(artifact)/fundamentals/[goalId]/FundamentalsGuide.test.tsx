// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { getFundamentalsGuide } from "@/lib/api-client";

import FundamentalsGuide from "./FundamentalsGuide";

vi.mock("next/navigation", () => ({
  useParams: () => ({ goalId: "rag-engineer" }),
}));

vi.mock("@/lib/api-client", () => ({
  getFundamentalsGuide: vi.fn(),
}));

const GUIDE = [
  "A production RAG system retrieves passages first, then asks the model to answer from those passages.",
  "",
  "## Retrieve before the model writes",
  "",
  "The question hits the store first.",
  "",
  "## Watch the retrieval loop",
  "",
  "https://www.youtube.com/watch?v=T-D1OfcDW1M",
  "",
].join("\n");

afterEach(() => {
  cleanup();
});

describe("Fundamentals guide", () => {
  it("shows the Goal, the guide, that guide's sections, and plays its YouTube video", async () => {
    vi.mocked(getFundamentalsGuide).mockImplementation(async (goalId, locale) => {
      expect(goalId).toBe("rag-engineer");
      expect(locale).toBe("en");
      return {
        goal_id: "rag-engineer",
        locale: "en",
        body_markdown: GUIDE,
      };
    });

    render(<FundamentalsGuide />);

    expect((await screen.findByTestId("fundamentals-goal")).textContent).toBe(
      "Production RAG & Advanced Retrieval",
    );
    const guide = screen.getByTestId("fundamentals-guide");
    expect(guide.textContent).toContain("The question hits the store first.");
    expect(guide.querySelector("#retrieve-before-the-model-writes")?.textContent).toBe(
      "Retrieve before the model writes",
    );

    const sections = screen.getByTestId("fundamentals-sections");
    const links = [...sections.querySelectorAll("a")].map((link) => ({
      text: link.textContent,
      href: link.getAttribute("href"),
    }));
    expect(links).toEqual([
      {
        text: "Retrieve before the model writes",
        href: "#retrieve-before-the-model-writes",
      },
      {
        text: "Watch the retrieval loop",
        href: "#watch-the-retrieval-loop",
      },
    ]);
    expect(sections.textContent).not.toContain("The question hits the store first.");

    const video = screen.getByTitle("YouTube video");
    expect(video.tagName).toBe("IFRAME");
    expect(video.getAttribute("src")).toBe(
      "https://www.youtube.com/embed/T-D1OfcDW1M",
    );
    expect(guide.contains(video)).toBe(true);
  });
});
