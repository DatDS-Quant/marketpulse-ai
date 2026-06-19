"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { KPIResponse } from "@/lib/types";
import { Target, TrendingUp } from "lucide-react";

export function ExecutiveSummary() {
  const [metrics, setMetrics] = useState<KPIResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMetrics()
      .then(res => {
        setMetrics(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full animate-pulse" />;
  }

  const topTrend = metrics?.cards?.find(c => c.key === "top_trend")?.value || "N/A";
  const confidence = metrics?.cards?.find(c => c.key === "average_confidence_score")?.value || 0;
  
  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-xl p-6 h-full shadow-sm flex flex-col justify-center relative overflow-hidden">
      <div className="absolute top-0 right-0 p-6 opacity-5 pointer-events-none">
        <Target className="w-32 h-32" />
      </div>
      
      <h2 className="text-sm font-bold uppercase tracking-widest text-blue-500 mb-2 flex items-center gap-2">
        <TrendingUp className="h-4 w-4" />
        Executive Summary
      </h2>
      
      {topTrend !== "N/A" ? (
        <>
          <p className="text-xl md:text-2xl font-medium text-slate-200 leading-relaxed mb-4 relative z-10">
            The strongest market signal currently is <span className="font-bold text-white bg-blue-500/20 px-2 py-0.5 rounded border border-blue-500/30">&quot;{topTrend}&quot;</span>.
          </p>
          <p className="text-slate-400 text-sm leading-relaxed relative z-10">
            Overall system confidence is running at <strong className="text-slate-300">{confidence} / 100</strong>. 
            Data pipelines are actively monitoring and validating this trend across available sources.
          </p>
        </>
      ) : (
        <p className="text-slate-400 italic">No sufficient data to generate an executive summary at this time.</p>
      )}
    </div>
  );
}
