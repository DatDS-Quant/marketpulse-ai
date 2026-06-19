import { SystemStatus } from "@/lib/types";
import { Server, CheckCircle2, AlertCircle } from "lucide-react";

export function SystemStatusSection({ status }: { status?: SystemStatus | null }) {
  if (!status) return null;

  const isStale = status.data_freshness === "stale" || status.data_freshness === "aging";

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full shadow-sm">
      <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-2">
        <Server className="h-5 w-5 text-slate-400" />
        System & Data Pipeline Health
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
          <p className="text-sm text-slate-400 mb-1">API Status</p>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            <p className="font-medium text-emerald-500 capitalize">{status.status}</p>
          </div>
        </div>
        <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
          <p className="text-sm text-slate-400 mb-1">Latest Run</p>
          <p className="font-medium text-slate-200">{status.latest_run_at ? new Date(status.latest_run_at).toLocaleString() : 'N/A'}</p>
        </div>
        <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
          <p className="text-sm text-slate-400 mb-1">Pipeline Quality</p>
          <p className="font-medium text-slate-200">{status.pipeline_metrics?.quality_score?.toFixed(1) || 'N/A'} / 100</p>
        </div>
        <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
          <p className="text-sm text-slate-400 mb-1">Data Freshness</p>
          <div className="flex items-center gap-2">
            {isStale ? (
              <AlertCircle className="h-4 w-4 text-amber-500" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            )}
            <p className={`font-medium capitalize ${isStale ? "text-amber-500" : "text-emerald-500"}`}>
              {status.data_freshness || "Unknown"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
