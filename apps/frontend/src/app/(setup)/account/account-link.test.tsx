// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import { confirmCareerForgeEmail, resetCareerForgePassword } from "@/lib/api-client";

import ConfirmCareerForgeAccountPage from "./confirm/page";
import ResetCareerForgePasswordPage from "./reset/page";

const navigation = vi.hoisted(() => ({
  push: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: navigation.push }),
}));

vi.mock("next/link", () => ({
  default: ({ children, href, ...rest }: { children: ReactNode; href: string }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/api-client", () => ({
  confirmCareerForgeEmail: vi.fn(),
  resetCareerForgePassword: vi.fn(),
}));

afterEach(() => {
  cleanup();
  navigation.push.mockReset();
  window.history.replaceState({}, "", "/");
});

describe("account link pages", () => {
  it("retries a confirmation that failed for another reason, without sending the learner to signup", async () => {
    window.history.replaceState({}, "", "/account/confirm?token=still-good");
    vi.mocked(confirmCareerForgeEmail)
      .mockRejectedValueOnce(new Error("API request failed: Could not send the email"))
      .mockResolvedValueOnce({
        access_token: "tok",
        token_type: "bearer",
        external_id: "user-1",
        provider: "email",
        expires_in: 3600,
      });

    render(<ConfirmCareerForgeAccountPage />);

    await waitFor(() => {
      expect(screen.getByTestId("account-link-failed").textContent).toBe(
        "Could not open the account. Try again.",
      );
    });
    expect(screen.queryByTestId("account-link-again")).toBeNull();

    fireEvent.click(screen.getByTestId("account-link-retry"));
    await waitFor(() => {
      expect(navigation.push).toHaveBeenCalledWith("/");
    });
    expect(confirmCareerForgeEmail).toHaveBeenNthCalledWith(2, "still-good");
  });

  it("sends an expired confirmation link back to signup", async () => {
    window.history.replaceState({}, "", "/account/confirm?token=used");
    vi.mocked(confirmCareerForgeEmail).mockRejectedValue(
      new Error("API request failed: This link has expired"),
    );

    render(<ConfirmCareerForgeAccountPage />);

    await waitFor(() => {
      expect(screen.getByTestId("account-link-again").getAttribute("href")).toBe(
        "/?account=signup",
      );
    });
  });

  it("keeps the new-password form when saving fails for another reason", async () => {
    window.history.replaceState({}, "", "/account/reset?token=still-good");
    vi.mocked(resetCareerForgePassword).mockRejectedValue(new Error("network down"));

    render(<ResetCareerForgePasswordPage />);
    fireEvent.change(screen.getByTestId("account-reset-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.change(screen.getByTestId("account-reset-confirm"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.click(screen.getByTestId("account-reset-submit"));

    await waitFor(() => {
      expect(screen.getByTestId("account-reset-error").textContent).toBe(
        "Could not save the new password. Try again.",
      );
    });
    expect(screen.queryByTestId("account-link-again")).toBeNull();
    expect(screen.getByTestId("account-reset-password")).toBeTruthy();
  });
});
