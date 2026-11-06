// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import { getCountries } from "libphonenumber-js";

import { IdentityGate } from "./IdentityGate";
import {
  AccountExistsError,
  EmailUnconfirmedError,
  MailDeliveryError,
  enterPilot,
  registerCareerForgeAccount,
  requestCareerForgePasswordReset,
  requestOtp,
  resendCareerForgeConfirmation,
  signInWithCareerForgePassword,
} from "@/lib/api-client";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...rest
  }: {
    children: ReactNode;
    href: string;
  }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/api-client", () => ({
  enterPilot: vi.fn(),
  requestOtp: vi.fn(),
  registerCareerForgeAccount: vi.fn(),
  resendCareerForgeConfirmation: vi.fn(),
  requestCareerForgePasswordReset: vi.fn(),
  signInWithCareerForgePassword: vi.fn(),
  verifyOtp: vi.fn(),
  OtpEmailOwnedError: class OtpEmailOwnedError extends Error {},
  AccountExistsError: class AccountExistsError extends Error {
    override name = "AccountExistsError";
  },
  EmailUnconfirmedError: class EmailUnconfirmedError extends Error {
    override name = "EmailUnconfirmedError";
  },
  MailDeliveryError: class MailDeliveryError extends Error {
    override name = "MailDeliveryError";
  },
}));

afterEach(() => {
  cleanup();
});

describe("IdentityGate freeze", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(enterPilot).mockResolvedValue({
      status: "promoted",
      access_token: "tok",
      token_type: "bearer",
      external_id: "user-pilot",
      provider: "email",
      expires_in: 3600,
    });
  });

  it("continues via pilot enter without requesting an OTP", async () => {
    const onVerified = vi.fn();
    render(<IdentityGate emailOtpRequired={false} onVerified={onVerified} />);

    expect(screen.getByTestId("identity-gate-topbar")).toBeTruthy();
    expect(screen.getByTestId("brand-lockup")).toBeTruthy();
    expect(screen.getByTestId("identity-gate-back-welcome").getAttribute("href")).toBe(
      "/welcome",
    );

    fireEvent.change(screen.getByTestId("identity-gate-email"), {
      target: { value: "pilot@example.com" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-continue"));

    await waitFor(() => {
      expect(enterPilot).toHaveBeenCalledWith("pilot@example.com");
      expect(onVerified).toHaveBeenCalled();
    });
    expect(requestOtp).not.toHaveBeenCalled();
    expect(screen.queryByTestId("identity-gate-request")).toBeNull();
  });
});

describe("IdentityGate password", () => {
  const forgotUrl = "https://platform.borderlesscoding.com/forgot-password";
  const signupUrl = "https://platform.borderlesscoding.com/sign-up";

  beforeEach(() => {
    window.history.pushState({}, "", "/");
    vi.clearAllMocks();
  });

  it("shows one sentence when Borderless sign-in did not finish", async () => {
    window.history.pushState({}, "", "/?oauth=failed");
    render(
      <IdentityGate method="borderless_password" onVerified={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByTestId("identity-gate-error").textContent).toBe(
        "Sign-in with Borderless did not finish. Try again.",
      );
    });
  });

  it("keeps Career Forge password and hides Borderless until OAuth is configured", () => {
    const { unmount } = render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );

    expect(screen.getByTestId("identity-gate-career-forge-password")).toBeTruthy();
    expect(screen.queryByTestId("identity-gate-password")).toBeNull();
    expect(screen.queryByTestId("identity-gate-signup-modal")).toBeNull();
    expect(screen.queryByTestId("identity-gate-signup")).toBeNull();
    expect(screen.queryByTestId("identity-gate-forgot")).toBeNull();
    expect(screen.queryByTestId("identity-gate-borderless")).toBeNull();
    expect(screen.getByTestId("identity-gate-topbar")).toBeTruthy();
    expect(screen.getByTestId("brand-lockup")).toBeTruthy();
    expect(screen.getByTestId("identity-gate-back-welcome").getAttribute("href")).toBe(
      "/welcome",
    );
    unmount();

    render(
      <IdentityGate
        method="borderless_password"
        borderlessOAuth
        onVerified={vi.fn()}
      />,
    );
    const link = screen.getByTestId("identity-gate-borderless");
    expect(link.tagName).toBe("A");
    expect(link.getAttribute("href")).toMatch(/\/auth\/borderless\/start$/);
    expect(screen.queryByTestId("identity-gate-password")).toBeNull();
    expect(screen.queryByTestId("identity-gate-signup-modal")).toBeNull();
  });

  it("signs in with a Career Forge password and creates an account without a code", async () => {
    const onVerified = vi.fn();
    vi.mocked(signInWithCareerForgePassword).mockResolvedValue({
      access_token: "cf-jwt",
      token_type: "bearer",
      external_id: "user-cf-password",
      provider: "email",
      expires_in: 3600,
    });
    vi.mocked(registerCareerForgeAccount).mockResolvedValue({
      ok: true,
      email: "ada@example.com",
    });
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={onVerified}
      />,
    );

    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signin"));
    await waitFor(() => {
      expect(signInWithCareerForgePassword).toHaveBeenCalledWith(
        "ada@example.com",
        "career-forge-secret",
      );
      expect(onVerified).toHaveBeenCalled();
    });
    expect(requestOtp).not.toHaveBeenCalled();

    fireEvent.click(screen.getByTestId("identity-gate-career-forge-create"));
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-name"), {
      target: { value: "Ada Lovelace" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-confirm"), {
      target: { value: "different-secret" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signup"));
    expect(registerCareerForgeAccount).not.toHaveBeenCalled();
    expect(screen.getByTestId("identity-gate-error").textContent).toBe(
      "Passwords do not match.",
    );

    fireEvent.change(screen.getByTestId("identity-gate-career-forge-confirm"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signup"));
    await waitFor(() => {
      expect(registerCareerForgeAccount).toHaveBeenCalledWith(
        "Ada Lovelace",
        "ada@example.com",
        "career-forge-secret",
      );
    });
    expect(screen.getByTestId("identity-gate-career-forge-sent").textContent).toContain(
      "ada@example.com",
    );
    expect(onVerified).toHaveBeenCalledTimes(1);
  });

  it("returns to Career Forge sign-in when the email already has an account", async () => {
    vi.mocked(registerCareerForgeAccount).mockRejectedValue(new AccountExistsError());
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByTestId("identity-gate-career-forge-create"));
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-name"), {
      target: { value: "Ada Lovelace" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-confirm"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signup"));

    await waitFor(() => {
      expect(screen.getByTestId("identity-gate-career-forge-signin")).toBeTruthy();
    });
    expect(screen.getByTestId("identity-gate-error").textContent).toBe(
      "This email already has an account.",
    );
    expect(screen.queryByTestId("identity-gate-borderless")).toBeNull();
    expect(screen.queryByTestId("identity-gate-signup-modal")).toBeNull();
  });

  it("offers a resend when the Career Forge password is not confirmed yet", async () => {
    vi.mocked(signInWithCareerForgePassword).mockRejectedValue(new EmailUnconfirmedError());
    vi.mocked(resendCareerForgeConfirmation).mockResolvedValue({
      ok: true,
      email: "ada@example.com",
    });
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signin"));
    await waitFor(() => {
      expect(screen.getByTestId("identity-gate-error").textContent).toBe(
        "Email is not confirmed.",
      );
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-resend"));
    await waitFor(() => {
      expect(resendCareerForgeConfirmation).toHaveBeenCalledWith("ada@example.com");
    });
  });

  it("offers resend when the confirmation email fails, without replacing the password", async () => {
    vi.mocked(registerCareerForgeAccount).mockRejectedValue(new MailDeliveryError());
    vi.mocked(resendCareerForgeConfirmation).mockResolvedValue({
      ok: true,
      email: "ada@example.com",
    });
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByTestId("identity-gate-career-forge-create"));
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-name"), {
      target: { value: "Ada Lovelace" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-confirm"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signup"));

    await waitFor(() => {
      expect(screen.getByTestId("identity-gate-error").textContent).toBe(
        "Could not send the email. Try again.",
      );
    });
    expect(screen.queryByTestId("identity-gate-career-forge-sent")).toBeNull();
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-resend"));
    await waitFor(() => {
      expect(resendCareerForgeConfirmation).toHaveBeenCalledWith("ada@example.com");
    });
    expect(registerCareerForgeAccount).toHaveBeenCalledTimes(1);
  });

  it("keeps the resend control when resend itself fails", async () => {
    vi.mocked(signInWithCareerForgePassword).mockRejectedValue(new EmailUnconfirmedError());
    vi.mocked(resendCareerForgeConfirmation).mockRejectedValue(new MailDeliveryError());
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signin"));
    await waitFor(() => {
      expect(screen.getByTestId("identity-gate-career-forge-resend")).toBeTruthy();
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-resend"));
    await waitFor(() => {
      expect(screen.getByTestId("identity-gate-error").textContent).toBe(
        "Could not send the email. Try again.",
      );
    });
    expect(screen.getByTestId("identity-gate-career-forge-resend")).toBeTruthy();
  });

  it("shows the same sentence after asking for a Career Forge password reset", async () => {
    vi.mocked(requestCareerForgePasswordReset).mockResolvedValue(undefined);
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByTestId("identity-gate-career-forge-forgot"));
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-forgot-submit"));
    await waitFor(() => {
      expect(requestCareerForgePasswordReset).toHaveBeenCalledWith("ada@example.com");
    });
    expect(screen.getByTestId("identity-gate-career-forge-notice").textContent).toBe(
      "If a confirmed Career Forge account exists for that email, we sent a link.",
    );
  });

  it("toggles password visibility", () => {
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );
    const field = screen.getByTestId("identity-gate-career-forge-password");
    expect(field.getAttribute("type")).toBe("password");
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-toggle-password"));
    expect(field.getAttribute("type")).toBe("text");
  });

  function fillCareerForgeSignup() {
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-create"));
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-name"), {
      target: { value: "Ada Lovelace" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-confirm"), {
      target: { value: "career-forge-secret" },
    });
  }

  it("sends a Brazilian number as E.164 and keeps a blank phone off the request", async () => {
    vi.mocked(registerCareerForgeAccount).mockResolvedValue({
      ok: true,
      email: "ada@example.com",
    });
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByTestId("identity-gate-career-forge-create"));
    const email = screen.getByTestId("identity-gate-career-forge-email");
    const country = screen.getByTestId("identity-gate-career-forge-phone-country");
    const national = screen.getByTestId("identity-gate-career-forge-phone");
    const password = screen.getByTestId("identity-gate-career-forge-password");
    expect(screen.getByText("Phone (optional)")).toBeTruthy();
    expect((country as HTMLInputElement).value).toBe("Brazil +55");
    expect(email.compareDocumentPosition(country) & Node.DOCUMENT_POSITION_FOLLOWING).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
    expect(national.compareDocumentPosition(password) & Node.DOCUMENT_POSITION_FOLLOWING).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );

    fireEvent.focus(country);
    expect(screen.getAllByRole("option")).toHaveLength(getCountries().length);
    fireEvent.change(country, { target: { value: "zzzz" } });
    expect(screen.queryAllByRole("option")).toHaveLength(0);
    fireEvent.blur(country);
    expect((country as HTMLInputElement).value).toBe("Brazil +55");

    fireEvent.change(national, { target: { value: "6502530000" } });
    fireEvent.focus(country);
    fireEvent.change(country, { target: { value: "United States" } });
    fireEvent.click(screen.getByRole("option", { name: "United States +1" }));
    expect((national as HTMLInputElement).value).toBe("6502530000");
    fireEvent.change(national, { target: { value: "(11) 98765-4321" } });
    fireEvent.focus(country);
    fireEvent.change(country, { target: { value: "Brazil" } });
    fireEvent.click(screen.getByRole("option", { name: "Brazil +55" }));

    fireEvent.change(screen.getByTestId("identity-gate-career-forge-name"), {
      target: { value: "Ada Lovelace" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-password"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-confirm"), {
      target: { value: "career-forge-secret" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signup"));
    await waitFor(() => {
      expect(registerCareerForgeAccount).toHaveBeenCalledWith(
        "Ada Lovelace",
        "ada@example.com",
        "career-forge-secret",
        "+5511987654321",
      );
    });
  });

  it("rejects an invalid phone and a number for another country before sign-up", () => {
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );
    fillCareerForgeSignup();
    fireEvent.change(screen.getByTestId("identity-gate-career-forge-phone"), {
      target: { value: "abc" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signup"));
    expect(registerCareerForgeAccount).not.toHaveBeenCalled();
    expect(screen.getByTestId("identity-gate-error").textContent).toBe(
      "Enter a valid phone number.",
    );

    fireEvent.change(screen.getByTestId("identity-gate-career-forge-phone"), {
      target: { value: "+1 650 253 0000" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-career-forge-signup"));
    expect(registerCareerForgeAccount).not.toHaveBeenCalled();
    expect(screen.getByTestId("identity-gate-error").textContent).toBe(
      "Enter a valid phone number.",
    );
  });

  it("names the phone field in Portuguese and still starts on Brazil", () => {
    (globalThis as { __cfLocale?: string }).__cfLocale = "pt-BR";
    try {
      render(
        <IdentityGate
          method="borderless_password"
          forgotPasswordUrl={forgotUrl}
          signupUrl={signupUrl}
          onVerified={vi.fn()}
        />,
      );
      fireEvent.click(screen.getByTestId("identity-gate-career-forge-create"));
      expect(screen.getByText("Telefone (opcional)")).toBeTruthy();
      expect(
        (screen.getByTestId("identity-gate-career-forge-phone-country") as HTMLInputElement).value,
      ).toBe("Brasil +55");
    } finally {
      delete (globalThis as { __cfLocale?: string }).__cfLocale;
    }
  });
});
