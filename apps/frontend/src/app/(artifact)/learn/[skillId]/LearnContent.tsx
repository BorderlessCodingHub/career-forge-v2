"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LearnContent() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/roadmap");
  }, [router]);

  return null;
}
