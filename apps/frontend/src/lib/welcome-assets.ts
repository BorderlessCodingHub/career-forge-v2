/** Public Welcome proof assets under `public/welcome/` (respects Next `basePath`). */

export function welcomeAssetPath(
  kind: "employers" | "mentors",
  filename: string,
): string {
  const base = (process.env.NEXT_PUBLIC_BASE_PATH ?? "").replace(/\/$/, "");
  const clean = filename.replace(/^\//, "");
  return `${base}/welcome/${kind}/${clean}`;
}
