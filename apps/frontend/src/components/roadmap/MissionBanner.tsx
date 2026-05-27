import type { PlanUpdateResponse } from "@/types/contracts";

type MissionBannerProps = {
  plan: PlanUpdateResponse;
};

export function MissionBanner({ plan }: MissionBannerProps) {
  return (
    <div
      className="mx-auto mt-8 max-w-3xl rounded-md border border-warning/40 bg-warning/10 px-5 py-4"
      data-testid="adaptive-mission-banner"
      data-screen="adaptive-state"
    >
      <p className="text-xs font-semibold uppercase tracking-widest text-warning">
        Trilha adaptada
      </p>
      <p className="mt-2 text-lg font-semibold text-text-primary">{plan.next_mission}</p>
      <p className="mt-2 text-sm text-text-secondary">{plan.today_focus.objective}</p>
      <p className="mt-3 text-xs text-text-muted">
        Foco de hoje · {plan.today_focus.duration_minutes} min · {plan.today_focus.title}
      </p>
    </div>
  );
}
