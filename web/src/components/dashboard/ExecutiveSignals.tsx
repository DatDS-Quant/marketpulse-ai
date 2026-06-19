/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { KPIResponse } from "@/lib/types";
import { BarChart2, Hash, Zap, ShieldCheck, Clock } from "lucide-react";
import { KpiCard } from "./KpiCard";

export function ExecutiveSignals() {
  const [metrics, setMetrics] = useState<KPIResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    api.getMetrics()
      .then(res => {
        setMetrics(res);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setError(true);
        setLoading(false);
      });
  }, []);

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-xl text-center">
        <p className="font-semibold text-lg">FastAPI backend is not reachable.</p>
        <p className="text-sm mt-2 opacity-80">Start it with <code>python -m uvicorn src.api.main:app --reload</code></p>
      </div>
    );
  }

  const getCardData = (key: string) => metrics?.cards?.find(c => c.key === key);

  const topTrend = getCardData("top_trend");
  const avgTrend = getCardData("average_trend_score");
  const avgConf = getCardData("average_confidence_score");
  const articles = getCardData("total_processed_articles");
  const freshness = getCardData("freshness_status");

  // Format helper to avoid "0" if data is missing, unless actually 0
  const formatValue = (val: any, fallback: string = "N/A") => {
    if (val === undefined || val === null || val === "N/A" || val === "") return fallback;
    return val;
  };

  const getStatusColor = (status?: string) => {
    if (status === "positive") return "text-emerald-400";
    if (status === "negative") return "text-red-400";
    return "text-slate-400";
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      <KpiCard 
        title="Top Trend" 
        value={formatValue(topTrend?.value)} 
        icon={Zap} 
        loading={loading}
        trend={topTrend?.status === "positive" ? "Surging" : "Stable"}
        trendColor={getStatusColor(topTrend?.status)}
      />
      <KpiCard 
        title="Avg Trend Score" 
        value={formatValue(avgTrend?.value)} 
        icon={BarChart2} 
        loading={loading}
        trend={avgTrend?.unit ? `out of 100` : ""}
        trendColor={getStatusColor(avgTrend?.status)}
      />
      <KpiCard 
        title="Avg Confidence" 
        value={formatValue(avgConf?.value)} 
        icon={ShieldCheck} 
        loading={loading}
        trend={avgConf?.unit ? `out of 100` : ""}
        trendColor={getStatusColor(avgConf?.status)}
      />
      <KpiCard 
        title="Processed Articles" 
        value={formatValue(articles?.value)} 
        icon={Hash} 
        loading={loading}
      />
      <KpiCard 
        title="Freshness" 
        value={formatValue(freshness?.value)} 
        icon={Clock} 
        loading={loading}
        trendColor={getStatusColor(freshness?.status)}
      />
    </div>
  );
}
