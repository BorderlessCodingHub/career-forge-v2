import { DiagnosticPills } from "@/components/diagnosis";
import { ProductEntryGate } from "@/components/auth";

export default function OnboardingPage() {
  return (
    <ProductEntryGate>
      <DiagnosticPills />
    </ProductEntryGate>
  );
}
