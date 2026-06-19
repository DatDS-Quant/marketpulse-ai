/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PaginatedResponse } from "@/lib/types";
import { FileText, ExternalLink, ChevronLeft, ChevronRight, AlertCircle, CheckCircle2 } from "lucide-react";

export function ArticlesSection() {
  const [data, setData] = useState<PaginatedResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    let active = true;
    api.getArticles(page, 5)
      .then(res => {
        if (active) {
          setData(res);
          setLoading(false);
        }
      })
      .catch(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, [page]);

  if (loading && !data) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm animate-pulse">
        <div className="h-6 w-48 bg-slate-800 rounded mb-6" />
        <div className="space-y-4">
          {[1,2,3].map(i => <div key={i} className="h-16 bg-slate-800 rounded" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
          <FileText className="h-6 w-6 text-slate-400" />
          Recent Articles Evidence
        </h2>
        {data && (
          <div className="text-sm font-medium text-slate-400 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/50">
            Total Validated: {data.total}
          </div>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="text-xs text-slate-400 uppercase bg-slate-800/50">
            <tr>
              <th className="px-4 py-3 rounded-tl-lg font-semibold tracking-wider">Title</th>
              <th className="px-4 py-3 font-semibold tracking-wider">Source</th>
              <th className="px-4 py-3 font-semibold tracking-wider">Matched Entity</th>
              <th className="px-4 py-3 font-semibold tracking-wider text-center">Quality</th>
              <th className="px-4 py-3 rounded-tr-lg text-right font-semibold tracking-wider">Link</th>
            </tr>
          </thead>
          <tbody>
            {data?.data?.map((article: any, idx: number) => {
              const qualityFlags = article.quality_flags || [];
              const hasFlags = Array.isArray(qualityFlags) && qualityFlags.length > 0;
              
              return (
                <tr key={idx} className="border-b border-slate-800/50 last:border-0 hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-4 font-medium text-slate-200">
                    <div className="line-clamp-2 max-w-sm leading-snug">{article.title}</div>
                    <div className="text-xs text-slate-500 mt-1">{article.published_at ? new Date(article.published_at).toLocaleDateString() : 'N/A'}</div>
                  </td>
                  <td className="px-4 py-4">{article.source_domain || article.source || 'Unknown'}</td>
                  <td className="px-4 py-4">
                    {article.keyword ? (
                      <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-1 rounded text-xs">
                        {article.keyword}
                      </span>
                    ) : (
                      <span className="text-slate-600">-</span>
                    )}
                  </td>
                  <td className="px-4 py-4 text-center">
                    {hasFlags ? (
                      <span title={qualityFlags.join(", ")} className="inline-flex items-center text-amber-500">
                        <AlertCircle className="h-4 w-4" />
                      </span>
                    ) : (
                      <span title="Valid" className="inline-flex items-center text-emerald-500">
                        <CheckCircle2 className="h-4 w-4" />
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-4 text-right">
                    {article.url ? (
                      <a href={article.url} target="_blank" rel="noopener noreferrer" className="inline-flex p-2 rounded-lg bg-slate-800/50 text-blue-400 hover:text-blue-300 hover:bg-slate-800 transition-colors">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    ) : (
                      <span className="text-slate-600">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
            {(!data?.data || data.data.length === 0) && (
              <tr>
                <td colSpan={5} className="px-4 py-12 text-center text-slate-500">
                  <FileText className="h-8 w-8 mx-auto mb-3 opacity-20" />
                  No articles found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-800">
          <span className="text-sm font-medium text-slate-400">
            Page {data.page} of {data.total_pages}
          </span>
          <div className="flex gap-2">
            <button 
              onClick={() => { setLoading(true); setPage(p => Math.max(1, p - 1)); }}
              disabled={page === 1 || loading}
              className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 disabled:opacity-50 hover:bg-slate-700 transition-colors"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <button 
              onClick={() => { setLoading(true); setPage(p => Math.min(data.total_pages, p + 1)); }}
              disabled={page === data.total_pages || loading}
              className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 disabled:opacity-50 hover:bg-slate-700 transition-colors"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
