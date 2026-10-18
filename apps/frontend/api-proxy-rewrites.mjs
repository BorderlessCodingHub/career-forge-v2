/**
 * API path prefixes proxied to the backend when API_INTERNAL_URL is set (prod compose).
 * With basePath, Next.js automatically prefixes rewrite `source` (e.g. /career-forge/diagnosis/...).
 * External `destination` URLs are not prefixed.
 *
 * `/billing/card` is an App Router page, so afterFiles leaves that path alone.
 * `/billing` and `/billing/:path*` (checkout, sync, portal, Stripe webhook) go to the API.
 */
const API_PREFIXES = [
  "auth",
  "operator",
  "me",
  "public",
  "diagnosis",
  "forge",
  "roadmap",
  "validation",
  "mentor",
  "mentor-report",
  "mock-interview",
  "demo",
  "knowledge-gaps",
  "tutor",
  "billing",
];

export function apiPrefixRewrites(internal) {
  const base = String(internal).replace(/\/$/, "");
  return API_PREFIXES.flatMap((prefix) => [
    {
      source: `/${prefix}`,
      destination: `${base}/${prefix}`,
    },
    {
      source: `/${prefix}/:path*`,
      destination: `${base}/${prefix}/:path*`,
    },
  ]);
}
