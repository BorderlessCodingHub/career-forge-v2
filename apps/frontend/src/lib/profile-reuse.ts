/** Hydrate onboarding session from persisted profile (CAR-29 diagnosis reuse). */

import {
  setAnswers,
  setMotivation,
  setSelectedGoal,
  setStoredDiagnosis,
  setYearsXp,
} from "@/lib/onboarding-session";
import type { MeProfileResponse, YearsXpRange } from "@/types/contracts";

function isYearsXp(value: unknown): value is YearsXpRange {
  return value === "0-1" || value === "1-3" || value === "3-5" || value === "5+";
}

/**
 * Write diagnosis + intake into sessionStorage for `/onboarding/edit`.
 * Returns true when goal + motivation are present (edit path is viable).
 */
export function hydrateOnboardingFromProfile(profile: MeProfileResponse): boolean {
  if (!profile.diagnosis) return false;
  setStoredDiagnosis(profile.diagnosis);

  const intake = profile.intake;
  if (!intake?.goal_id || !intake.motivation?.trim()) {
    return false;
  }
  setSelectedGoal(intake.goal_id);
  setMotivation(intake.motivation);
  if (isYearsXp(intake.years_xp)) {
    setYearsXp(intake.years_xp);
  }
  if (intake.answers && Object.keys(intake.answers).length > 0) {
    setAnswers(intake.answers);
  }
  return true;
}
