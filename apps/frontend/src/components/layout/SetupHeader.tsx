"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { SignOutButton } from "@/components/auth/SignOutButton";
import { BrandLockup } from "@/components/ui/BrandLockup";
import { shouldShowSetupHeader } from "@/lib/product-chrome";
import { hasEmailIdentity } from "@/lib/user-session";

export function SetupHeader() {
  const pathname = usePathname();
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    setSignedIn(hasEmailIdentity());
  }, []);

  if (!shouldShowSetupHeader(pathname, signedIn)) return null;

  return (
    <header
      className="flex items-center justify-between border-b border-border bg-bg-sidebar px-6 py-3"
      data-testid="setup-topbar"
    >
      <BrandLockup />
      <SignOutButton />
    </header>
  );
}
