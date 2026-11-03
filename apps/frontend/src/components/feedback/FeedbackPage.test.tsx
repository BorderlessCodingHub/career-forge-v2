// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import { FeedbackPage } from "./FeedbackPage";
import { FeedbackLink } from "./FeedbackLink";
import { SetupHeader } from "@/components/layout/SetupHeader";
import { ArtifactShell } from "@/components/layout/ArtifactShell";

const session = vi.hoisted(() => ({
  signedIn: true,
  email: "ana@example.com" as string | null,
}));

const navigation = vi.hoisted(() => ({
  pathname: "/roadmap",
}));

vi.mock("next/navigation", () => ({
  usePathname: () => navigation.pathname,
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("next/link", () => ({
  default: ({ children, href, ...rest }: { children: ReactNode; href: string }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/user-session", () => ({
  hasEmailIdentity: () => session.signedIn,
  signOut: vi.fn(),
}));

vi.mock("@/lib/api-client", () => {
  class FeedbackLimitError extends Error {
    readonly name = "FeedbackLimitError";
  }
  return {
    FeedbackLimitError,
    getMyProfile: vi.fn(async () => ({ email: session.email })),
    submitLearnerFeedback: vi.fn(async () => undefined),
    updateMyLocale: vi.fn(),
  };
});

import { FeedbackLimitError, submitLearnerFeedback } from "@/lib/api-client";

function renderWithLocale(node: ReactNode, locale: "en" | "pt-BR" = "en") {
  if (locale === "pt-BR") {
    (globalThis as { __cfLocale?: string }).__cfLocale = "pt-BR";
  } else {
    delete (globalThis as { __cfLocale?: string }).__cfLocale;
  }
  return render(<NextIntlClientProvider locale={locale}>{node}</NextIntlClientProvider>);
}

afterEach(() => {
  cleanup();
  session.signedIn = true;
  session.email = "ana@example.com";
  navigation.pathname = "/roadmap";
  delete (globalThis as { __cfLocale?: string }).__cfLocale;
  vi.clearAllMocks();
});

describe("feedback page", () => {
  it("sends one message, thanks the learner, and clears the box", async () => {
    renderWithLocale(<FeedbackPage />);

    expect(await screen.findByTestId("feedback-email")).toHaveProperty(
      "textContent",
      "ana@example.com",
    );
    expect(screen.getByTestId("feedback-courtesy").textContent).toBe(
      "A person will reply within 5 business days.",
    );
    expect(screen.queryByRole("textbox", { name: /email/i })).toBeNull();

    fireEvent.change(screen.getByTestId("feedback-message"), {
      target: { value: "The timeline is the part I trust." },
    });
    fireEvent.click(screen.getByTestId("feedback-submit"));

    await waitFor(() => {
      expect(submitLearnerFeedback).toHaveBeenCalledWith({
        message: "The timeline is the part I trust.",
        path: "/",
      });
    });
    expect(screen.getByTestId("feedback-thanks").textContent).toBe("Thank you. The note is in.");
    expect(screen.getByTestId("feedback-courtesy").textContent).toContain("5 business days");
    expect((screen.getByTestId("feedback-message") as HTMLTextAreaElement).value).toBe("");
  });

  it("keeps the text when a sixth note is rejected", async () => {
    vi.mocked(submitLearnerFeedback).mockRejectedValueOnce(new FeedbackLimitError());
    renderWithLocale(<FeedbackPage />);
    const box = await screen.findByTestId("feedback-message");
    fireEvent.change(box, { target: { value: "Still here" } });
    fireEvent.click(screen.getByTestId("feedback-submit"));

    expect(await screen.findByTestId("feedback-error")).toHaveProperty(
      "textContent",
      "Five notes are already in from this account in the last 24 hours. This one stayed on the page.",
    );
    expect((screen.getByTestId("feedback-message") as HTMLTextAreaElement).value).toBe("Still here");
    expect(screen.queryByTestId("feedback-thanks")).toBeNull();
  });

  it("rejects an empty message and leaves the box as it is", async () => {
    renderWithLocale(<FeedbackPage />);
    const box = await screen.findByTestId("feedback-message");
    fireEvent.change(box, { target: { value: "   " } });
    fireEvent.click(screen.getByTestId("feedback-submit"));

    expect(await screen.findByTestId("feedback-error")).toHaveProperty(
      "textContent",
      "Write a message.",
    );
    expect(submitLearnerFeedback).not.toHaveBeenCalled();
    expect((screen.getByTestId("feedback-message") as HTMLTextAreaElement).value).toBe("   ");
  });

  it("explains a direct visit when the account has no email", async () => {
    session.email = null;
    renderWithLocale(<FeedbackPage />);
    expect(await screen.findByTestId("feedback-blocked")).toHaveProperty(
      "textContent",
      "This account has no email, so a note cannot be sent.",
    );
    expect(screen.queryByTestId("feedback-message")).toBeNull();
  });

  it("gives a signed-out visitor no form", async () => {
    session.signedIn = false;
    renderWithLocale(<FeedbackPage />);
    expect(await screen.findByTestId("feedback-blocked")).toHaveProperty(
      "textContent",
      "Sign in with an account email to leave a note.",
    );
    expect(screen.queryByTestId("feedback-message")).toBeNull();
    expect(screen.queryByTestId("feedback-submit")).toBeNull();
  });

  it("follows the Portuguese catalog", async () => {
    renderWithLocale(<FeedbackPage />, "pt-BR");
    expect((await screen.findByTestId("feedback-courtesy")).textContent).toBe(
      "Uma pessoa responde em até 5 dias úteis.",
    );
  });
});

describe("feedback link", () => {
  it("sits next to sign out in both bars only when the account has an email", async () => {
    navigation.pathname = "/onboarding";
    renderWithLocale(<SetupHeader />);
    const link = await screen.findByTestId("feedback-link");
    expect(link.getAttribute("href")).toBe("/feedback?from=%2Fonboarding");
    expect(link.compareDocumentPosition(screen.getByTestId("sign-out-button"))).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
    cleanup();

    navigation.pathname = "/roadmap";
    renderWithLocale(<ArtifactShell>trail</ArtifactShell>);
    const artifactLink = await screen.findByTestId("feedback-link");
    expect(artifactLink.getAttribute("href")).toBe("/feedback?from=%2Froadmap");
    expect(
      artifactLink.compareDocumentPosition(screen.getByTestId("sign-out-button")),
    ).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
    cleanup();

    session.email = null;
    renderWithLocale(<SetupHeader />);
    await waitFor(() => {
      expect(screen.queryByTestId("feedback-link")).toBeNull();
    });
    expect(screen.getByTestId("sign-out-button")).toBeTruthy();
    cleanup();

    session.signedIn = false;
    navigation.pathname = "/welcome";
    renderWithLocale(<SetupHeader />);
    expect(screen.queryByTestId("feedback-link")).toBeNull();
    expect(screen.queryByTestId("setup-topbar")).toBeNull();
  });
});
