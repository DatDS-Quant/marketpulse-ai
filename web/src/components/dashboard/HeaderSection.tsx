import { SystemStatus } from "@/lib/types";
import { Activity, CheckCircle, XCircle, AlertTriangle, Clock } from "lucide-react";

export function HeaderSection({ status, loading, error }: { status?: SystemStatus | null, loading: boolean, error: boolean }) {
  const normalizedStatus = status?.status?.toLowerCase() ?? "unknown";
  const isHealthy = normalizedStatus === "online" || normalizedStatus === "healthy";
  
  return (
    <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
          <Activity className="h-8 w-8 text-blue-500" />
          MarketPulse AI Console
        </h1>
        <p className="text-slate-400 mt-1">Intelligence, Trends, and Automated Insights.</p>
      </div>

      <div className="mt-4 md:mt-0 flex items-center gap-4 bg-slate-900 border border-slate-800 p-3 rounded-lg">
        <div className="flex flex-col text-right">
          <span className="text-xs text-slate-500 font-medium uppercase tracking-wider">System Status</span>
          <div className="text-sm font-medium flex items-center justify-end min-w-[100px]">
            {loading ? (
              <span className="text-slate-400 flex items-center gap-1">
                <Clock className="h-4 w-4 animate-spin"/> Loading...
              </span>
            ) : error ? (
              <span className="text-red-500 flex items-center gap-1">
                <XCircle className="h-4 w-4"/> Disconnected
              </span>
            ) : (
              <span className={`flex items-center gap-1 ${isHealthy ? 'text-emerald-500' : 'text-amber-500'}`}>
                <span className="flex-shrink-0 flex items-center">
                  {isHealthy ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                </span>
                <span>{normalizedStatus.toUpperCase()}</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
