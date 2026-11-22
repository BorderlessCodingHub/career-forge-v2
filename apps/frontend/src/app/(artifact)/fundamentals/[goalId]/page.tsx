"use client";

import { ProductEntryGate } from "@/components/auth";

import FundamentalsGuide from "./FundamentalsGuide";

export default function FundamentalsPage() {
  return (
    <ProductEntryGate>
      <FundamentalsGuide />
    </ProductEntryGate>
  );
}
