import { Info } from "lucide-react";

interface MetricExplainerProps {
  metrics: {
    label: string;
    description: string;
  }[];
}

export function MetricExplainer({ metrics }: MetricExplainerProps) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <Info className="h-4 w-4 text-blue-400" />
        Understanding these metrics
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m, idx) => (
          <div key={idx} className="bg-slate-950/50 rounded-lg p-3 border border-slate-800/50">
            <div className="text-xs font-medium text-slate-200 mb-1">{m.label}</div>
            <div className="text-xs text-slate-400 leading-relaxed">{m.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
