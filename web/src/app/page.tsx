"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { SystemStatus } from "@/lib/types";
import { HeaderSection } from "@/components/dashboard/HeaderSection";
import { ExecutiveSignals } from "@/components/dashboard/ExecutiveSignals";
import { ExecutiveSummary } from "@/components/dashboard/ExecutiveSummary";
import { SystemStatusSection } from "@/components/dashboard/SystemStatusSection";
import { InsightSection } from "@/components/dashboard/InsightSection";

export default function Dashboard() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    // Health check first
    api.getSystemStatus()
      .then(res => {
        setStatus(res);
        setLoading(false);
      })
      .catch(e => {
        console.error("Dashboard init error:", e);
        setError(true);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <HeaderSection status={status} loading={loading} error={error} />
      
      {/* Row 1: 5 compact KPI cards */}
      <ExecutiveSignals />

      {/* Row 2: Executive Summary & System Freshness */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ExecutiveSummary />
        </div>
        <div className="lg:col-span-1">
          <SystemStatusSection status={status} />
        </div>
      </div>

      {/* Row 3: Insight Signals */}
      <div>
        <InsightSection />
      </div>
    </div>
  );
}
