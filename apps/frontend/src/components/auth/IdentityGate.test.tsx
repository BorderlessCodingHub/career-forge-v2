// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

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
  signInWithPassword,
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
  signInWithPassword: vi.fn(),
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
    vi.clearAllMocks();
    vi.mocked(signInWithPassword).mockResolvedValue({
      access_token: "cf-jwt",
      token_type: "bearer",
      external_id: "user-password",
      provider: "email",
      expires_in: 3600,
    });
  });

  it("signs in via Career Forge and never requests OTP", async () => {
    const onVerified = vi.fn();
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={onVerified}
      />,
    );

    fireEvent.change(screen.getByTestId("identity-gate-email"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.change(screen.getByTestId("identity-gate-password"), {
      target: { value: "secret-pass" },
    });
    fireEvent.click(screen.getByTestId("identity-gate-signin"));

    await waitFor(() => {
      expect(signInWithPassword).toHaveBeenCalledWith("ada@example.com", "secret-pass");
      expect(onVerified).toHaveBeenCalled();
    });
    expect(requestOtp).not.toHaveBeenCalled();
    expect(enterPilot).not.toHaveBeenCalled();
    expect(screen.queryByTestId("identity-gate-request")).toBeNull();
    expect(screen.getByTestId("identity-gate-topbar")).toBeTruthy();
    expect(screen.getByTestId("brand-lockup")).toBeTruthy();
    expect(screen.getByTestId("identity-gate-back-welcome").getAttribute("href")).toBe(
      "/welcome",
    );
    expect(screen.getByTestId("identity-gate-forgot").getAttribute("href")).toBe(forgotUrl);
    expect(screen.getByTestId("identity-gate-forgot").getAttribute("target")).toBe("_blank");
  });

  it("opens signup modal then Borderless sign-up in a new tab", () => {
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl={forgotUrl}
        signupUrl={signupUrl}
        onVerified={vi.fn()}
      />,
    );

    expect(screen.queryByTestId("identity-gate-signup-modal")).toBeNull();
    fireEvent.click(screen.getByTestId("identity-gate-signup"));
    expect(screen.getByTestId("identity-gate-signup-modal")).toBeTruthy();

    const openBorderless = screen.getByTestId("identity-gate-signup-open-borderless");
    expect(openBorderless.getAttribute("href")).toBe(signupUrl);
    expect(openBorderless.getAttribute("target")).toBe("_blank");

    fireEvent.click(screen.getByTestId("identity-gate-signup-already"));
    expect(screen.queryByTestId("identity-gate-signup-modal")).toBeNull();
  });

  it("hides account links when URLs are empty", () => {
    render(
      <IdentityGate
        method="borderless_password"
        forgotPasswordUrl=""
        signupUrl=""
        onVerified={vi.fn()}
      />,
    );
    expect(screen.getByTestId("identity-gate-password")).toBeTruthy();
    expect(screen.queryByTestId("identity-gate-forgot")).toBeNull();
    expect(screen.queryByTestId("identity-gate-signup")).toBeNull();
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

    fireEvent.click(screen.getByTestId("identity-gate-career-forge"));
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
    expect(signInWithPassword).not.toHaveBeenCalled();
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

    fireEvent.click(screen.getByTestId("identity-gate-career-forge"));
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
    expect(screen.getByTestId("identity-gate-back-borderless")).toBeTruthy();
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

    fireEvent.click(screen.getByTestId("identity-gate-career-forge"));
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

    fireEvent.click(screen.getByTestId("identity-gate-career-forge"));
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

    fireEvent.click(screen.getByTestId("identity-gate-career-forge"));
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

    fireEvent.click(screen.getByTestId("identity-gate-career-forge"));
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
    const field = screen.getByTestId("identity-gate-password");
    expect(field.getAttribute("type")).toBe("password");
    fireEvent.click(screen.getByTestId("identity-gate-toggle-password"));
    expect(field.getAttribute("type")).toBe("text");
  });
});
