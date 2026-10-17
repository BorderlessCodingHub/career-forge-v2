import { LegalDocument } from "@/components/legal/LegalDocument";

import { legalMetadata } from "../metadata";

export function generateMetadata() {
  return legalMetadata("terms");
}

export default function TermsPage() {
  return <LegalDocument page="terms" />;
}
