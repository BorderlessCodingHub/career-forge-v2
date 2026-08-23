/** Canonical paywall copy (CAR-46) — keep in sync with backend PaywallError. */
export const PAYWALL_COPY =
  "Subscribe to start diagnosis and forge your roadmap";

export class PaywallError extends Error {
  readonly code = "paywall" as const;
  readonly checkoutAvailable: boolean;

  constructor(checkoutAvailable: boolean, message = PAYWALL_COPY) {
    super(message);
    this.name = "PaywallError";
    this.checkoutAvailable = checkoutAvailable;
  }
}

export function isPaywallError(err: unknown): err is PaywallError {
  return err instanceof PaywallError;
}

export function paywallErrorFromResponse(
  status: number,
  body: { detail?: unknown },
): PaywallError | null {
  if (status !== 402) return null;
  const detail = body.detail;
  const checkoutAvailable =
    Boolean(
      detail &&
        typeof detail === "object" &&
        "checkout_available" in detail &&
        (detail as { checkout_available?: unknown }).checkout_available === true,
    );
  const message =
    detail &&
    typeof detail === "object" &&
    "message" in detail &&
    typeof (detail as { message?: unknown }).message === "string"
      ? (detail as { message: string }).message
      : PAYWALL_COPY;
  return new PaywallError(checkoutAvailable, message);
}
