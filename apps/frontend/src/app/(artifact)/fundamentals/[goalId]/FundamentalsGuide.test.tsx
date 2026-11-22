// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ArtifactShell } from "@/components/layout/ArtifactShell";
import { getFundamentalsGuide } from "@/lib/api-client";
import type { Locale } from "@/lib/locale";

import FundamentalsGuide from "./FundamentalsGuide";

const navigation = vi.hoisted(() => ({
  refresh: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ goalId: "rag-engineer" }),
  usePathname: () => "/fundamentals/rag-engineer",
  useRouter: () => ({ push: vi.fn(), refresh: navigation.refresh }),
}));

vi.mock("next/link", () => ({
  default: ({ children, href, ...rest }: { children: ReactNode; href: string }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
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

const PORTUGUESE = [
  "Um sistema de RAG em produção recupera passagens primeiro e só então pede ao modelo que responda a partir dessas passagens.",
  "",
  "## Recupere antes de o modelo escrever",
  "",
  "A pergunta chega ao acervo primeiro.",
  "",
  "## Observe o ciclo de recuperação",
  "",
  "https://www.youtube.com/watch?v=PtBrRagVid1",
  "",
].join("\n");

function localeCookie(): string | undefined {
  return document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith("cf_locale="))
    ?.slice("cf_locale=".length);
}

/** The signed-in page: the shell's locale control refreshes, and that refresh is the locale. */
function SignedInGuide() {
  const [locale, setLocale] = useState<Locale>("pt-BR");
  (globalThis as { __cfLocale?: string }).__cfLocale = locale;
  useEffect(() => {
    navigation.refresh.mockImplementation(() => {
      setLocale(localeCookie() === "pt-BR" ? "pt-BR" : "en");
    });
  }, []);
  return (
    <ArtifactShell>
      <FundamentalsGuide />
    </ArtifactShell>
  );
}

afterEach(() => {
  cleanup();
  navigation.refresh.mockReset();
  delete (globalThis as { __cfLocale?: string }).__cfLocale;
  document.cookie = "cf_locale=; Path=/; Max-Age=0";
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

  it("opens the Portuguese edition for the same Goal and follows the locale control back to English", async () => {
    vi.mocked(getFundamentalsGuide).mockImplementation(async (goalId, locale) => {
      if (goalId !== "rag-engineer") throw new Error(`opened ${goalId}`);
      if (locale === "pt-BR") {
        return {
          goal_id: "rag-engineer",
          locale: "pt-BR",
          body_markdown: PORTUGUESE,
        };
      }
      if (locale === "en") {
        return {
          goal_id: "rag-engineer",
          locale: "en",
          body_markdown: GUIDE,
        };
      }
      throw new Error(`unexpected locale ${locale}`);
    });
    vi.mocked(getFundamentalsGuide).mockClear();

    render(<SignedInGuide />);

    expect((await screen.findByTestId("fundamentals-goal")).textContent).toBe(
      "RAG de produção e recuperação avançada",
    );
    const guide = screen.getByTestId("fundamentals-guide");
    expect(guide.textContent).toContain("A pergunta chega ao acervo primeiro.");
    expect(guide.querySelector("h2")?.textContent).toBe(
      "Recupere antes de o modelo escrever",
    );
    expect(screen.getByTitle("YouTube video").getAttribute("src")).toBe(
      "https://www.youtube.com/embed/PtBrRagVid1",
    );
    expect(screen.getByTestId("fundamentals").querySelector("[data-testid='locale-switch']")).toBeNull();
    const control = screen.getByTestId("locale-switch");
    expect(screen.getByTestId("artifact-topbar").contains(control)).toBe(true);
    expect(screen.getAllByTestId("locale-switch")).toHaveLength(1);

    fireEvent.click(screen.getByTestId("locale-switch-en"));

    expect(localeCookie()).toBe("en");
    expect((await screen.findByTestId("fundamentals-goal")).textContent).toBe(
      "Production RAG & Advanced Retrieval",
    );
    const english = screen.getByTestId("fundamentals-guide");
    expect(english.textContent).toContain("The question hits the store first.");
    expect(english.textContent).not.toContain("A pergunta chega ao acervo primeiro.");
    expect(screen.getByTitle("YouTube video").getAttribute("src")).toBe(
      "https://www.youtube.com/embed/T-D1OfcDW1M",
    );
    expect(screen.getByTestId("fundamentals").querySelector("[data-testid='locale-switch']")).toBeNull();
    expect(
      vi.mocked(getFundamentalsGuide).mock.calls.every(([goalId]) => goalId === "rag-engineer"),
    ).toBe(true);
    expect(vi.mocked(getFundamentalsGuide).mock.calls.map(([, locale]) => locale)).toEqual([
      "pt-BR",
      "en",
    ]);
  });
});
