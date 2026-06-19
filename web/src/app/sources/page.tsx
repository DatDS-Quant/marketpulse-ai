import { SourceSection } from "@/components/dashboard/SourceSection";
import { MetricExplainer } from "@/components/dashboard/MetricExplainer";
import { ShieldCheck } from "lucide-react";

export default function SourcesPage() {
  const metrics = [
    {
      label: "Quality Score",
      description: "Computed score (0-100) analyzing historical data completeness, missing fields, and broken links from a source."
    },
    {
      label: "Article Volume",
      description: "The total number of articles ingested from this particular source during the current timeframe."
    },
    {
      label: "Highly Reliable",
      description: "Sources with a quality score ≥ 80. These provide consistent, fully formed metadata and valid links."
    },
    {
      label: "Unreliable",
      description: "Sources with a quality score < 50. Frequently missing titles, content, or providing broken URLs."
    }
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
          <ShieldCheck className="h-8 w-8 text-emerald-500" />
          Source Reliability
        </h1>
        <p className="text-slate-400 mt-2 text-lg">
          Can we trust the sources behind the detected trends?
        </p>
      </div>

      <MetricExplainer metrics={metrics} />
      
      <SourceSection />
    </div>
  );
}
