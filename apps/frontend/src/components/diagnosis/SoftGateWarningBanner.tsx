"use client";

type SoftGateWarningBannerProps = {
  warning: string;
  testId?: string;
};

/** Soft-gate copy from API — presentation only (CAR-15). */
export function SoftGateWarningBanner({
  warning,
  testId = "soft-gate-warning",
}: SoftGateWarningBannerProps) {
  return (
    <div
      className="rounded-md border border-warning/30 bg-warning/5 px-4 py-3 text-sm text-text-secondary"
      data-testid={testId}
      role="status"
    >
      <p className="text-xs font-semibold uppercase tracking-widest text-warning">
        Lean roadmap
      </p>
      <p className="mt-1 text-text-primary">{warning}</p>
    </div>
  );
}
