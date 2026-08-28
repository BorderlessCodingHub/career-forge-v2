/** Canonical figure assets under `public/learn/` (respects Next `basePath`). */

export function learnAssetSrc(src: string): string {
  const base = (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
  if (!base || src.startsWith(`${base}/`)) {
    return src;
  }
  return `${base}${src}`;
}
