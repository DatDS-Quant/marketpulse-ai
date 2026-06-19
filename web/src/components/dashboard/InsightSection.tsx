/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { InsightSeed, ChartResponse } from "@/lib/types";
import { Lightbulb, AlertTriangle, Info, ShieldAlert, Cpu } from "lucide-react";

export function InsightSection() {
  const [insights, setInsights] = useState<InsightSeed[]>([]);
  const [topTrends, setTopTrends] = useState<ChartResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getInsightSeeds().catch(() => ({ data: [] })),
      api.getTopTrends().catch(() => null)
    ]).then(([seedsRes, trendsRes]) => {
      setInsights(seedsRes.data || []);
      setTopTrends(trendsRes);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8 animate-pulse">
        <div className="h-6 w-48 bg-slate-800 rounded mb-4" />
        <div className="space-y-4">
          <div className="h-24 bg-slate-800 rounded-lg" />
        </div>
      </div>
    );
  }

  // Fallback to deterministic signals from Top Trends if no explicit insight seeds
  let displayInsights: any[] = insights;
  let isFallback = false;

  if (displayInsights.length === 0 && topTrends && topTrends.data && topTrends.data.length > 0) {
    isFallback = true;
    displayInsights = topTrends.data.slice(0, 3).map((trend: any, idx: number) => {
      const conf = trend.confidence_score || 0;
      const severity = conf > 80 ? "low" : conf > 50 ? "medium" : "high"; // low severity = good confidence
      
      return {
        rule_id: `derived-trend-${idx}`,
        category: "Market Signal",
        severity: severity,
        headline: `${trend.keyword} shows strong market activity`,
        description: `'${trend.keyword}' is a leading market signal with a trend score of ${trend.trend_score?.toFixed(1) || 0} and confidence score of ${conf?.toFixed(1) || 0}, supported by ${trend.article_count || 0} recent articles.`,
        limitation: conf < 60 ? "Confidence score is relatively low, indicating potential noise or single-source dependency." : "No significant limitations detected. Signal appears robust.",
        next_step: "Monitor the keyword in the next run and review supporting articles in Evidence Explorer.",
        metric_value: trend.trend_score,
        date_generated: new Date().toISOString().split('T')[0]
      };
    });
  }

  if (displayInsights.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8 text-center text-slate-500">
        <Lightbulb className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No actionable insights generated yet.</p>
        <p className="text-sm mt-1">Run ingestion → ETL → analytics → trends first.</p>
      </div>
    );
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'high': return <ShieldAlert className="h-5 w-5 text-red-400" />;
      case 'medium': return <AlertTriangle className="h-5 w-5 text-amber-400" />;
      case 'low': return <Info className="h-5 w-5 text-blue-400" />;
      default: return <Lightbulb className="h-5 w-5 text-slate-400" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'high': return 'border-red-500/30 bg-red-500/5';
      case 'medium': return 'border-amber-500/30 bg-amber-500/5';
      case 'low': return 'border-blue-500/30 bg-blue-500/5';
      default: return 'border-slate-700 bg-slate-800/50';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full shadow-sm">
      <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-2">
        {isFallback ? <Cpu className="h-6 w-6 text-blue-400" /> : <Lightbulb className="h-6 w-6 text-amber-400" />}
        {isFallback ? "Deterministic Insight Signals" : "AI-ready Insight Signals"}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {displayInsights.map((insight, idx) => (
          <div key={idx} className={`p-5 rounded-xl border flex flex-col justify-between ${getSeverityColor(insight.severity)} hover:border-opacity-80 transition-colors`}>
            <div>
              <div className="flex items-start justify-between mb-4">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 bg-slate-950/50 px-2 py-1 rounded">
                  {insight.category}
                </span>
                {getSeverityIcon(insight.severity)}
              </div>
              <h3 className="text-slate-100 font-semibold text-lg leading-snug mb-3">{insight.headline}</h3>
              
              <div className="space-y-3 mt-4">
                <div>
                  <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1">Factual Explanation</span>
                  <p className="text-sm text-slate-400 leading-relaxed">{insight.description}</p>
                </div>
                
                {(insight.limitation || insight.description.includes("Limitation")) && (
                  <div>
                    <span className="text-xs font-semibold text-amber-500/80 uppercase tracking-wider block mb-1">Limitation</span>
                    <p className="text-sm text-slate-400 leading-relaxed">{insight.limitation || "Review underlying sources for full context."}</p>
                  </div>
                )}
                
                {insight.next_step && (
                  <div className="bg-slate-950/30 p-3 rounded border border-slate-800/50 mt-2">
                    <span className="text-xs font-semibold text-emerald-500/80 uppercase tracking-wider block mb-1">Practical Next Step</span>
                    <p className="text-sm text-slate-300 leading-relaxed">{insight.next_step}</p>
                  </div>
                )}
              </div>
            </div>
            
            {insight.metric_value && (
              <div className="mt-5 pt-4 border-t border-slate-700/50 flex justify-between items-center text-xs text-slate-500 font-medium">
                <span className="bg-slate-950/50 px-2 py-1 rounded">Score: {Number(insight.metric_value).toFixed(1)}</span>
                <span>{insight.date_generated}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
