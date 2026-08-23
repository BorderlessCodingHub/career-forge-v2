/** Product chrome visibility rules (CAR-70). */

export function isMarketingRoute(pathname: string): boolean {
  return pathname === "/welcome" || pathname === "/welcome/plg";
}

export function isResumeRoute(pathname: string): boolean {
  return pathname.startsWith("/resume/");
}

export function isShareRoute(pathname: string): boolean {
  return pathname.startsWith("/share/");
}

export function shouldShowSetupHeader(pathname: string, signedIn: boolean): boolean {
  if (isMarketingRoute(pathname)) return false;
  if (isResumeRoute(pathname)) return false;
  return signedIn;
}

export function shouldShowArtifactShell(pathname: string, signedIn: boolean): boolean {
  if (isShareRoute(pathname)) return true;
  return signedIn;
}
