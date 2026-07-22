/** Canonical kill-switch copy (CAR-6) — keep in sync with backend QuotaExhaustedError. */
export const QUOTA_EXHAUSTED_COPY =
  "experimental quota exhausted — come back on day 1 of next month";

export function isQuotaExhaustedMessage(message: string): boolean {
  return message.toLowerCase().includes("experimental quota exhausted");
}

export function toUserFacingApiError(status: number, detail: string): string {
  if (status === 429 || isQuotaExhaustedMessage(detail)) {
    return QUOTA_EXHAUSTED_COPY;
  }
  return `API request failed: ${detail}`;
}
