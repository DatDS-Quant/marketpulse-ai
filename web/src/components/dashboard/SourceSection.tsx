/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ChartResponse } from "@/lib/types";
import { ShieldCheck, ScatterChart as ScatterIcon } from "lucide-react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, ScatterChart, Scatter, ZAxis
} from "recharts";

const CustomBarTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const source = payload[0].payload;
    const qualityScore = source.source_quality_score || source.reliability_score || 0;
    return (
      <div className="bg-slate-950 border border-slate-700 p-4 rounded-lg shadow-xl">
        <p className="text-slate-200 font-bold mb-2">{label}</p>
        <p className="text-sm font-medium text-slate-300 mb-1">
          Articles: {source.article_count}
        </p>
        <p className={`text-sm font-bold mt-2 ${qualityScore >= 80 ? 'text-emerald-400' : qualityScore >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
          Quality Score: {Number(qualityScore).toFixed(1)} / 100
        </p>
      </div>
    );
  }
  return null;
};

const CustomScatterTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const source = payload[0].payload;
    const qualityScore = source.source_quality_score || source.reliability_score || 0;
    return (
      <div className="bg-slate-950 border border-slate-700 p-4 rounded-lg shadow-xl">
        <p className="text-slate-200 font-bold mb-2">{source.source || source.source_domain}</p>
        <p className="text-sm font-medium text-slate-300 mb-1">
          Articles (Volume): {source.article_count}
        </p>
        <p className={`text-sm font-bold mt-2 ${qualityScore >= 80 ? 'text-emerald-400' : qualityScore >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
          Quality Score: {Number(qualityScore).toFixed(1)} / 100
        </p>
      </div>
    );
  }
  return null;
};

export function SourceSection() {
  const [data, setData] = useState<ChartResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSources()
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          <div className="h-[450px] bg-slate-900 border border-slate-800 rounded-xl" />
          <div className="h-[450px] bg-slate-900 border border-slate-800 rounded-xl" />
        </div>
      </div>
    );
  }

  if (!data || !data.data || data.data.length === 0) {
    return null;
  }

  const chartData = [...data.data].sort((a, b) => b.article_count - a.article_count).slice(0, 10);
  
  // Format for scatter chart
  const scatterData = data.data.map(d => ({
    ...d,
    fill: (d.source_quality_score || 0) >= 80 ? "#10b981" : (d.source_quality_score || 0) >= 50 ? "#f59e0b" : "#ef4444"
  }));

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-emerald-500" />
            Top Sources by Volume
          </h2>
          
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={true} vertical={false} />
                <XAxis 
                  type="number" 
                  stroke="#64748b" 
                  fontSize={12} 
                  tickLine={false} 
                  axisLine={false}
                />
                <YAxis 
                  type="category" 
                  dataKey={data.data[0].source ? "source" : "source_domain"} 
                  stroke="#94a3b8" 
                  fontSize={13}
                  fontWeight={500}
                  tickLine={false} 
                  axisLine={false}
                  width={120}
                />
                <RechartsTooltip content={<CustomBarTooltip />} cursor={{ fill: '#1e293b', opacity: 0.5 }} />
                <Bar 
                  dataKey="article_count" 
                  name="Articles"
                  radius={[0, 4, 4, 0]} 
                  barSize={24}
                >
                  {chartData.map((entry, index) => {
                    const qs = entry.source_quality_score || entry.reliability_score || 0;
                    return <Cell key={`cell-${index}`} fill={qs >= 80 ? "#10b981" : qs >= 50 ? "#f59e0b" : "#ef4444"} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 flex justify-center gap-6 text-xs font-medium text-slate-400">
            <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Highly Reliable (≥80)</span>
            <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-amber-500"></span> Moderately Reliable (50-79)</span>
            <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> Unreliable (&lt;50)</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-2">
            <ScatterIcon className="h-6 w-6 text-blue-500" />
            Volume vs Quality Comparison
          </h2>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis 
                  type="number" 
                  dataKey="article_count" 
                  name="Volume" 
                  stroke="#94a3b8"
                  label={{ value: "Article Volume", position: "insideBottom", offset: -10, fill: "#64748b" }}
                />
                <YAxis 
                  type="number" 
                  dataKey="source_quality_score" 
                  name="Quality" 
                  stroke="#94a3b8"
                  domain={[0, 100]}
                  label={{ value: "Quality Score", angle: -90, position: "insideLeft", fill: "#64748b" }}
                />
                <ZAxis type="number" range={[100, 300]} />
                <RechartsTooltip content={<CustomScatterTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Sources" data={scatterData} fill="#8884d8" opacity={0.8} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-slate-400" />
          Source Reliability Data
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs text-slate-400 uppercase bg-slate-800/50">
              <tr>
                <th className="px-4 py-3 rounded-tl-lg font-semibold tracking-wider">Source</th>
                <th className="px-4 py-3 font-semibold tracking-wider text-right">Articles</th>
                <th className="px-4 py-3 font-semibold tracking-wider text-right">Quality Score</th>
                <th className="px-4 py-3 rounded-tr-lg font-semibold tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((item: any, idx: number) => {
                const qs = item.source_quality_score || item.reliability_score || 0;
                const sourceName = item.source || item.source_domain || "Unknown";
                return (
                  <tr key={idx} className="border-b border-slate-800/50 last:border-0 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-4 font-medium text-slate-200">{sourceName}</td>
                    <td className="px-4 py-4 text-right">{item.article_count}</td>
                    <td className={`px-4 py-4 text-right font-medium ${qs >= 80 ? 'text-emerald-400' : qs >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                      {Number(qs).toFixed(1)}
                    </td>
                    <td className="px-4 py-4">
                      {qs >= 80 ? (
                        <span className="bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded text-xs border border-emerald-500/20">Highly Reliable</span>
                      ) : qs >= 50 ? (
                        <span className="bg-amber-500/10 text-amber-400 px-2 py-1 rounded text-xs border border-amber-500/20">Moderate</span>
                      ) : (
                        <span className="bg-red-500/10 text-red-400 px-2 py-1 rounded text-xs border border-red-500/20">Unreliable</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
