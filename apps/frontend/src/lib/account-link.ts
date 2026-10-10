/** True only when the API refused the link as expired or already used. */
export function isExpiredAccountLink(err: unknown): boolean {
  return err instanceof Error && err.message.includes("This link has expired");
}
