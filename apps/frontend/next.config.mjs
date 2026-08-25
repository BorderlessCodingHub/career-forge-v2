/** Public path when served behind labs.borderlesscoding.com (or similar). */
const BASE_PATH = "/career-forge";

/**
 * API path prefixes proxied to the backend when API_INTERNAL_URL is set (prod compose).
 * With basePath, Next.js automatically prefixes rewrite `source` (e.g. /career-forge/diagnosis/...).
 * External `destination` URLs are not prefixed.
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
];

/** @type {import('next').NextConfig} */
const nextConfig = {
  basePath: BASE_PATH,
  env: {
    // Same-origin fetch("/diagnosis/...") must include basePath; Link/router already do.
    NEXT_PUBLIC_BASE_PATH: BASE_PATH,
  },
  output: "standalone",
  async redirects() {
    // CAR-56 / CAR-52: Premium B is now App Router `/welcome`; old bake-off URL → canonical.
    return [
      {
        source: "/welcome/premium-b",
        destination: "/welcome",
        permanent: true,
      },
      {
        source: "/welcome/premium-b/",
        destination: "/welcome",
        permanent: true,
      },
    ];
  },
  async rewrites() {
    // Must be available at `next build` (Docker builder). Runtime-only compose
    // env is too late — empty rewrites → /career-forge/health 404 on Labs.
    const internal = (
      process.env.API_INTERNAL_URL?.trim() || "http://backend:8000"
    ).replace(/\/$/, "");

    return {
      // CAR-41: Premium A bake-off clone — before App Router.
      // Premium B rewrite removed (CAR-56); redirect → /welcome instead.
      beforeFiles: [
        {
          source: "/welcome/premium-a",
          destination: "/premium-landings/a.html",
        },
        {
          source: "/welcome/premium-a/",
          destination: "/premium-landings/a.html",
        },
      ],
      afterFiles: [
        // `/reference` is an App Router page; proxy only its learner allowlist API child.
        {
          source: "/reference/embed-hosts",
          destination: `${internal}/reference/embed-hosts`,
        },
        // Exact prefix roots first — POST /forge, POST /validation, etc. do not match /:path*
        ...API_PREFIXES.flatMap((prefix) => [
          {
            source: `/${prefix}`,
            destination: `${internal}/${prefix}`,
          },
          {
            source: `/${prefix}/:path*`,
            destination: `${internal}/${prefix}/:path*`,
          },
        ]),
        // Exact health check (footer badge).
        {
          source: "/health",
          destination: `${internal}/health`,
        },
      ],
    };
  },
};

export default nextConfig;
