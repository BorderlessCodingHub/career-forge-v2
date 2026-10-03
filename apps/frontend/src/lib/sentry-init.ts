import * as Sentry from "@sentry/nextjs";

/** Errors + tracing. Email is stripped. No learner feedback widget. */
export function initSentry(): void {
  const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN?.trim();
  if (!dsn) return;

  const release =
    process.env.NEXT_PUBLIC_SENTRY_RELEASE?.trim() ||
    process.env.NEXT_PUBLIC_BUILD_SHA?.trim() ||
    undefined;

  Sentry.init({
    dsn,
    environment:
      process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT?.trim() ||
      (process.env.NODE_ENV === "production" ? "labs" : "local"),
    release,
    sendDefaultPii: false,
    tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,
    beforeSend(event) {
      delete event.user;
      return event;
    },
  });
}
