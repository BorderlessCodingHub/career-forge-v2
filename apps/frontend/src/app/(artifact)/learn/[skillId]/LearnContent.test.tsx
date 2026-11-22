// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getCanonicalContent } from "@/lib/api-client";

import LearnContent from "./LearnContent";

const navigation = vi.hoisted(() => ({
  router: { replace: vi.fn() },
  skillId: "rag-chunking",
  notFound: vi.fn(() => {
    throw new Error("NEXT_NOT_FOUND");
  }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => navigation.router,
  useParams: () => ({ skillId: navigation.skillId }),
  notFound: () => navigation.notFound(),
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

  it("does not present the skill lesson and does not open the Roadmap", () => {
    expect(() => render(<LearnContent />)).toThrow("NEXT_NOT_FOUND");
    expect(navigation.notFound).toHaveBeenCalled();
    expect(navigation.router.replace).not.toHaveBeenCalled();
    expect(screen.queryByTestId("canonical-learn")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Chunking for RAG" })).toBeNull();
    expect(screen.queryByText("Split documents for retrieval.")).toBeNull();
  });
});
