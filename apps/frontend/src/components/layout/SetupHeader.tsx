"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { BrandLockup } from "@/components/ui/BrandLockup";
import { shouldShowSetupHeader } from "@/lib/product-chrome";
import { hasEmailIdentity } from "@/lib/user-session";

import { learnerTopbarClass, LearnerTopbarActions } from "./LearnerTopbarActions";

export function SetupHeader() {
  const pathname = usePathname();
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    setSignedIn(hasEmailIdentity());
  }, []);

  if (!shouldShowSetupHeader(pathname, signedIn)) return null;

  return (
    <header className={learnerTopbarClass} data-testid="setup-topbar">
      <BrandLockup markSize={28} className="shrink-0" />
      <LearnerTopbarActions fundamentals feedback signOut />
    </header>
  );
}
