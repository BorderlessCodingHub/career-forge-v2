/** API path prefixes proxied to the backend when API_INTERNAL_URL is set (prod compose). */
const API_PREFIXES = [
  "diagnosis",
  "forge",
  "roadmap",
  "validation",
  "mentor",
  "mentor-report",
  "mock-interview",
  "demo",
];

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    const internal = process.env.API_INTERNAL_URL?.replace(/\/$/, "");
    if (!internal) return [];

    return API_PREFIXES.map((prefix) => ({
      source: `/${prefix}/:path*`,
      destination: `${internal}/${prefix}/:path*`,
    }));
  },
};

export default nextConfig;
