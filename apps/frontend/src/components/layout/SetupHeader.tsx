"use client";

import { useEffect, useState } from "react";

import { SignOutButton } from "@/components/auth/SignOutButton";
import { hasEmailIdentity } from "@/lib/user-session";

export function SetupHeader() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(hasEmailIdentity());
  }, []);

  if (!visible) return null;

  return (
    <header
      className="flex items-center justify-end border-b border-border bg-bg-sidebar px-6 py-3"
      data-testid="setup-topbar"
    >
      <SignOutButton />
    </header>
  );
}
