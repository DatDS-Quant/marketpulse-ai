/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ChartResponse } from "@/lib/types";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend
} from "recharts";
import { TrendingUp, Activity } from "lucide-react";

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-950 border border-slate-700 p-4 rounded-lg shadow-xl">
        <p className="text-slate-200 font-bold mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm font-medium" style={{ color: entry.color }}>
            {entry.name}: {Number(entry.value).toFixed(1)}
          </p>
        ))}
        {payload[0]?.payload?.article_count && (
          <p className="text-sm text-slate-400 mt-1 font-medium">Articles: {payload[0].payload.article_count}</p>
        )}
      </div>
    );
  }
  return null;
};

export function TrendSection() {
  const [topTrends, setTopTrends] = useState<ChartResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Only need top trends for both charts as per user instructions
    api.getTopTrends()
      .then(top => {
        setTopTrends(top);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-[450px] bg-slate-900 border border-slate-800 rounded-xl animate-pulse" />
        <div className="h-[450px] bg-slate-900 border border-slate-800 rounded-xl animate-pulse" />
      </div>
    );
  }

  if (!topTrends || !topTrends.data || topTrends.data.length === 0) {
    return null;
  }

  const config = topTrends.chart_config;
  const data = topTrends.data.slice(0, 10); // Top 10 only
  const top5Data = topTrends.data.slice(0, 5); // Top 5 for confidence comparison

  const renderHorizontalTopTrends = () => {
    return (
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={data} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={true} vertical={false} />
          <XAxis 
            type="number"
            stroke="#64748b" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false} 
          />
          <YAxis 
            dataKey={config.x_axis_key} 
            type="category"
            stroke="#94a3b8" 
            fontSize={13}
            fontWeight={500}
            tickLine={false} 
            axisLine={false} 
            width={100}
          />
          <RechartsTooltip content={<CustomTooltip />} cursor={{ fill: '#1e293b', opacity: 0.5 }} />
          <Bar 
            dataKey="trend_score" 
            name="Trend Score"
            fill="#3b82f6" 
            radius={[0, 4, 4, 0]} 
            barSize={24}
          />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderConfidenceComparison = () => {
    return (
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={top5Data} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis 
            dataKey={config.x_axis_key} 
            stroke="#94a3b8" 
            fontSize={13}
            fontWeight={500}
            tickLine={false} 
            axisLine={false} 
          />
          <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
          <RechartsTooltip content={<CustomTooltip />} cursor={{ fill: '#1e293b', opacity: 0.5 }} />
          <Legend wrapperStyle={{ fontSize: '13px', paddingTop: '20px', color: '#cbd5e1' }} iconType="circle" />
          <Bar 
            dataKey="trend_score" 
            name="Trend Score"
            fill="#3b82f6" 
            radius={[4, 4, 0, 0]} 
            barSize={32}
          />
          <Bar 
            dataKey="confidence_score" 
            name="Confidence Score"
            fill="#10b981" 
            radius={[4, 4, 0, 0]} 
            barSize={32}
          />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-blue-500" />
            Top Market Trends Ranking
          </h2>
          {renderHorizontalTopTrends()}
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-2">
            <Activity className="h-6 w-6 text-emerald-500" />
            Trend Score vs Confidence
          </h2>
          {renderConfidenceComparison()}
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-slate-400" />
          Trend Data
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs text-slate-400 uppercase bg-slate-800/50">
              <tr>
                <th className="px-4 py-3 rounded-tl-lg font-semibold tracking-wider">Keyword</th>
                <th className="px-4 py-3 font-semibold tracking-wider">Trend Score</th>
                <th className="px-4 py-3 font-semibold tracking-wider">Confidence</th>
                <th className="px-4 py-3 font-semibold tracking-wider">Articles</th>
                <th className="px-4 py-3 rounded-tr-lg font-semibold tracking-wider">Signal Type</th>
              </tr>
            </thead>
            <tbody>
              {topTrends.data.map((item: any, idx: number) => (
                <tr key={idx} className="border-b border-slate-800/50 last:border-0 hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-4 font-medium text-blue-400">{item.keyword}</td>
                  <td className="px-4 py-4 text-slate-200">{Number(item.trend_score).toFixed(1)}</td>
                  <td className="px-4 py-4 text-emerald-400">{Number(item.confidence_score).toFixed(1)}</td>
                  <td className="px-4 py-4 text-slate-300">{item.article_count}</td>
                  <td className="px-4 py-4 text-slate-400">{item.signal_type || "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
