import { EditableDiagnosis } from "@/components/diagnosis";
import { ProductEntryGate } from "@/components/auth";

export default function OnboardingEditPage() {
  return (
    <ProductEntryGate>
      <EditableDiagnosis />
    </ProductEntryGate>
  );
}
