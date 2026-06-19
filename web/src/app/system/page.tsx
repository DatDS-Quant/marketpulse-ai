"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { SystemStatus } from "@/lib/types";
import { SystemStatusSection } from "@/components/dashboard/SystemStatusSection";
import { MetricExplainer } from "@/components/dashboard/MetricExplainer";
import { Activity } from "lucide-react";

export default function SystemPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSystemStatus()
      .then(res => {
        setStatus(res);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const metrics = [
    {
      label: "API Status",
      description: "Indicates whether the FastAPI backend is running and responding to requests."
    },
    {
      label: "Latest Run",
      description: "The timestamp of the most recent successful execution of the data pipeline."
    },
    {
      label: "Pipeline Quality",
      description: "Overall data quality score calculated during the ETL phase."
    },
    {
      label: "Data Freshness",
      description: "Warns if the data is getting old (Aging) or outdated (Stale) based on the collection schedule."
    }
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
          <Activity className="h-8 w-8 text-emerald-500" />
          System Health
        </h1>
        <p className="text-slate-400 mt-2 text-lg">
          Is the pipeline healthy enough to trust the dashboard?
        </p>
      </div>

      <MetricExplainer metrics={metrics} />
      
      <div className="animate-in fade-in duration-500 delay-150">
        {loading ? (
          <div className="h-64 bg-slate-900 border border-slate-800 rounded-xl animate-pulse" />
        ) : (
          <div className="max-w-3xl">
            <SystemStatusSection status={status} />
            
            {status?.data_freshness && (status.data_freshness === 'aging' || status.data_freshness === 'stale') && (
               <div className="mt-6 bg-amber-500/10 border border-amber-500/20 rounded-xl p-5 text-amber-400">
                 <h3 className="font-semibold mb-2 text-amber-500">Pipeline Instructions</h3>
                 <p className="text-sm">The dashboard data is marked as <strong>{status.data_freshness}</strong>. To refresh the metrics, run the following commands in your backend environment:</p>
                 <pre className="mt-3 bg-slate-950 p-3 rounded text-xs border border-slate-800 text-slate-300">
                   python -m src.collectors.run_ingestion{'\n'}
                   python -m src.processing.run_etl{'\n'}
                   python -m src.analytics.run_analytics{'\n'}
                   python -m src.intelligence.run_trends
                 </pre>
               </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
