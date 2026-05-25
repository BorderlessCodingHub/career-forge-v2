"use client";

import { useEffect, useState } from "react";

import { MentorReportView } from "@/components/mentor-report/MentorReportView";
import { getMentorReport } from "@/lib/api-client";
import { getUserId } from "@/lib/user-session";
import type { MentorReportResponse } from "@/types/contracts";

export function MentorReportContent() {
  const [report, setReport] = useState<MentorReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await getMentorReport(getUserId());
        if (!cancelled) setReport(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Falha ao carregar relatório");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-sm text-text-muted">
        Carregando relatório para mentor…
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-sm text-warning">{error ?? "Relatório indisponível"}</p>
      </div>
    );
  }

  return <MentorReportView report={report} />;
}
