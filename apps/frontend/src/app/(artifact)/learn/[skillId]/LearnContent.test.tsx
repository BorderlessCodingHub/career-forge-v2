// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getCanonicalContent } from "@/lib/api-client";

import LearnContent from "./LearnContent";

const navigation = vi.hoisted(() => ({
  router: { replace: vi.fn() },
  skillId: "rag-chunking",
}));

vi.mock("next/navigation", () => ({
  useRouter: () => navigation.router,
  useParams: () => ({ skillId: navigation.skillId }),
}));

vi.mock("@/lib/api-client", () => ({
  getCanonicalContent: vi.fn(),
}));

afterEach(() => {
  cleanup();
  navigation.router.replace.mockReset();
  navigation.skillId = "rag-chunking";
});

describe("LearnContent", () => {
  beforeEach(() => {
    vi.mocked(getCanonicalContent).mockResolvedValue({
      skill_id: "rag-chunking",
      title: "Chunking for RAG",
      url: null,
      body_markdown: "# Body\n\nSplit documents for retrieval.",
    });
  });

  it("renders published canonical markdown", async () => {
    render(<LearnContent />);

    expect(await screen.findByTestId("canonical-learn")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Chunking for RAG" })).toBeTruthy();
    expect(screen.getByText("Split documents for retrieval.")).toBeTruthy();
    expect(screen.getByTestId("learn-return-to-roadmap").getAttribute("href")).toBe(
      "/roadmap",
    );
  });

  it("renders figure, callout, and reveals quiz why on pick", async () => {
    vi.mocked(getCanonicalContent).mockResolvedValue({
      skill_id: "rag-embeddings",
      title: "Embeddings fundamentals",
      url: null,
      body_markdown: [
        "> **The win.**",
        "> Same map on both sides.",
        "",
        "![Tube map](/learn/rag-embeddings-tube.svg)",
        "",
        "```quiz",
        "The vector of a chunk stores:",
        "- A) position on the learned map",
        "- B) a compressed copy of the text",
        "correct: A",
        "why: The vector is a position, not a compression of the text.",
        "```",
      ].join("\n"),
    });

    render(<LearnContent />);

    const figure = await screen.findByRole("img", { name: "Tube map" });
    expect(figure.getAttribute("src")).toBe("/learn/rag-embeddings-tube.svg");
    expect(screen.getByText("The win.")).toBeTruthy();
    expect(screen.getByText("Same map on both sides.")).toBeTruthy();
    expect(screen.queryByText(/The vector is a position/)).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /position on the learned map/i }));

    expect(screen.getByText(/Correct\./)).toBeTruthy();
    expect(screen.getByText(/The vector is a position, not a compression of the text/)).toBeTruthy();
  });

  it("serves the figure under the deployed basePath", async () => {
    process.env.NEXT_PUBLIC_BASE_PATH = "/career-forge";
    vi.mocked(getCanonicalContent).mockResolvedValue({
      skill_id: "rag-embeddings",
      title: "Embeddings fundamentals",
      url: null,
      body_markdown: "![Tube map](/learn/rag-embeddings-tube-map.svg)\n",
    });

    render(<LearnContent />);

    const figure = await screen.findByRole("img", { name: "Tube map" });
    expect(figure.getAttribute("src")).toBe(
      "/career-forge/learn/rag-embeddings-tube-map.svg",
    );

    delete process.env.NEXT_PUBLIC_BASE_PATH;
  });

  it("marks a wrong quiz pick as incorrect and still shows why", async () => {
    vi.mocked(getCanonicalContent).mockResolvedValue({
      skill_id: "rag-embeddings",
      title: "Embeddings fundamentals",
      url: null,
      body_markdown: [
        "```quiz",
        "The vector of a chunk stores:",
        "- A) position on the learned map",
        "- B) a compressed copy of the text",
        "correct: A",
        "why: The vector is a position, not a compression of the text.",
        "```",
      ].join("\n"),
    });

    render(<LearnContent />);

    fireEvent.click(
      await screen.findByRole("button", { name: /compressed copy of the text/i }),
    );

    expect(screen.getByText(/Incorrect\./)).toBeTruthy();
    expect(screen.getByText(/The vector is a position, not a compression of the text/)).toBeTruthy();
  });

  it("omits unsafe figures and broken quizzes without crashing", async () => {
    vi.mocked(getCanonicalContent).mockResolvedValue({
      skill_id: "rag-chunking",
      title: "Chunking for RAG",
      url: null,
      body_markdown: "![x](javascript:alert(1))\n\n```quiz\nbroken\n```\n\nSafe paragraph.\n",
    });

    render(<LearnContent />);

    expect(await screen.findByText("Safe paragraph.")).toBeTruthy();
    expect(screen.queryByRole("img")).toBeNull();
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("returns to the Roadmap when the canônico is missing", async () => {
    vi.mocked(getCanonicalContent).mockRejectedValue(new Error("not found"));

    render(<LearnContent />);

    await waitFor(() => {
      expect(navigation.router.replace).toHaveBeenCalledWith("/roadmap");
    });
    expect(screen.queryByTestId("canonical-learn")).toBeNull();
  });
});
