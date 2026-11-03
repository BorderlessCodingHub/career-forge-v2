import type { Metadata } from "next";

import { FeedbackPage } from "@/components/feedback/FeedbackPage";

export const metadata: Metadata = {
  title: "Feedback · Career Forge",
  robots: { index: false, follow: false },
};

export default function FeedbackRoute() {
  return <FeedbackPage />;
}
