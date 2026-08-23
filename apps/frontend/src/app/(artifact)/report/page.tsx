import { MentorReportContent } from "./MentorReportContent";
import { ProductEntryGate } from "@/components/auth";

export default function MentorReportPage() {
  return (
    <ProductEntryGate>
      <MentorReportContent />
    </ProductEntryGate>
  );
}
