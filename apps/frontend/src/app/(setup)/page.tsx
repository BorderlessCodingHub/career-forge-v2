import { LandingRecoveryGate } from "@/components/recovery";
import { ProductEntryGate } from "@/components/auth";

export default function GoalPage() {
  return (
    <ProductEntryGate>
      <LandingRecoveryGate />
    </ProductEntryGate>
  );
}
