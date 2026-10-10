import { CAREER_GOALS } from "@/lib/onboarding-data";

const TRACK_MESSAGE_KEYS = {
  "rag-engineer": "trackRag",
  "agent-engineer": "trackAgent",
  "llm-evals": "trackEvals",
  "fine-tuning": "trackTune",
} as const;

export type TrackMessageKey = (typeof TRACK_MESSAGE_KEYS)[keyof typeof TRACK_MESSAGE_KEYS];

export function trackMessageKey(goalIdOrTitle: string): TrackMessageKey | null {
  const trimmed = goalIdOrTitle.trim();
  if (trimmed in TRACK_MESSAGE_KEYS) {
    return TRACK_MESSAGE_KEYS[trimmed as keyof typeof TRACK_MESSAGE_KEYS];
  }
  const byTitle = CAREER_GOALS.find((goal) => goal.title === trimmed);
  if (byTitle && byTitle.id in TRACK_MESSAGE_KEYS) {
    return TRACK_MESSAGE_KEYS[byTitle.id as keyof typeof TRACK_MESSAGE_KEYS];
  }
  return null;
}
