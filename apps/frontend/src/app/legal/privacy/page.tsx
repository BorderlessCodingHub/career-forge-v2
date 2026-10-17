import { LegalDocument } from "@/components/legal/LegalDocument";

import { legalMetadata } from "../metadata";

export function generateMetadata() {
  return legalMetadata("privacy");
}

export default function PrivacyPage() {
  return <LegalDocument page="privacy" />;
}
