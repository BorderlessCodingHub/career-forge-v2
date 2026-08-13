/** Public brand kit under `public/brand/` (respects Next `basePath`). */

export function brandAssetPath(filename: string): string {
  const base = (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
  const clean = filename.replace(/^\//, "");
  return `${base}/brand/${clean}`;
}

export const BRAND_LOGO_SVG = "borderless-logo.svg";
export const BRAND_FAVICON = "favicon.ico";
