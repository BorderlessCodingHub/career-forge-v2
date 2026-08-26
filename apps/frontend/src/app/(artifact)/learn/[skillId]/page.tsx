"use client";

import { ProductEntryGate } from "@/components/auth";

import LearnContent from "./LearnContent";

export default function LearnPage() {
  return (
    <ProductEntryGate>
      <LearnContent />
    </ProductEntryGate>
  );
}
