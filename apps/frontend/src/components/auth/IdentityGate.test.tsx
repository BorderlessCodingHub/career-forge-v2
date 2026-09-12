// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import { IdentityGate } from "./IdentityGate";
import { enterPilot, requestOtp, signInWithPassword } from "@/lib/api-client";

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
  verifyOtp: vi.fn(),
  signInWithPassword: vi.fn(),
  OtpEmailOwnedError: class OtpEmailOwnedError extends Error {},
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
