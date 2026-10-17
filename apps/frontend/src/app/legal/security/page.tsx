import { LegalDocument } from "@/components/legal/LegalDocument";

import { legalMetadata } from "../metadata";

export function generateMetadata() {
  return legalMetadata("security");
}

export default function SecurityPage() {
  return <LegalDocument page="security" />;
}
