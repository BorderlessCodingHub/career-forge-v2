/** Build/deploy metadata baked at image build time (NEXT_PUBLIC_*). */

export type ApiHealthState = "ok" | "degraded" | "unreachable" | "loading";

function getPublicBackendUrl(): string {
  const fromEnv =
    process.env.NEXT_PUBLIC_BACKEND_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim();
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  return "";
}

export function shortBuildSha(sha: string | undefined): string {
  const trimmed = sha?.trim();
  if (!trimmed) return "";
  return trimmed.slice(0, 7);
}

export function formatBuildTime(iso: string | undefined): string {
  const trimmed = iso?.trim();
  if (!trimmed) return "";
  const date = new Date(trimmed);
  if (Number.isNaN(date.getTime())) return trimmed;
  return date.toLocaleString("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

export function getDeployBadgeLabel(): string {
  const sha = process.env.NEXT_PUBLIC_BUILD_SHA?.trim();
  if (!sha) return "local dev";

  const shortSha = shortBuildSha(sha);
  const time = formatBuildTime(process.env.NEXT_PUBLIC_BUILD_TIME);
  if (time) return `deploy ${shortSha} · ${time}`;
  return `deploy ${shortSha}`;
}

export function apiHealthLabel(state: ApiHealthState): string {
  switch (state) {
    case "ok":
      return "API ok";
    case "degraded":
      return "API degraded";
    case "unreachable":
      return "API unreachable";
    default:
      return "API checking…";
  }
}

export async function fetchApiHealthState(): Promise<ApiHealthState> {
  const base = getPublicBackendUrl();
  const url = base ? `${base}/health` : "/health";

  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return "unreachable";
    const body = (await res.json()) as { status?: string };
    if (body.status === "ok") return "ok";
    if (body.status === "degraded") return "degraded";
    return "unreachable";
  } catch {
    return "unreachable";
  }
}
