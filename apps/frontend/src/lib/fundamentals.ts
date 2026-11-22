/** A screen is a Roadmap only at the roadmap trail. Everywhere else opens the first published guide. */
export function isRoadmapScreen(pathname: string): boolean {
  return pathname === "/roadmap" || pathname.startsWith("/roadmap/");
}

export function fundamentalsPath(goalId: string): string {
  return `/fundamentals/${encodeURIComponent(goalId)}`;
}
