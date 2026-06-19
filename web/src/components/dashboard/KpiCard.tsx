import { LucideIcon } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  trendColor?: string;
  loading?: boolean;
}

export function KpiCard({ title, value, icon: Icon, trend, trendColor, loading }: KpiCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm flex flex-col justify-between hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-400">{title}</span>
        <Icon className="h-5 w-5 text-slate-500" />
      </div>
      <div className="mt-4 flex items-baseline justify-between">
        {loading ? (
          <div className="h-8 w-24 bg-slate-800 rounded animate-pulse" />
        ) : (
          <span className="text-3xl font-bold text-slate-100">{value}</span>
        )}
        {trend && !loading && (
          <span className={`text-sm font-medium ${trendColor || "text-slate-400"}`}>
            {trend}
          </span>
        )}
      </div>
    </div>
  );
}
