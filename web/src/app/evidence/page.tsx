import { ArticlesSection } from "@/components/dashboard/ArticlesSection";
import { MetricExplainer } from "@/components/dashboard/MetricExplainer";
import { FileText } from "lucide-react";

export default function EvidencePage() {
  const metrics = [
    {
      label: "Evidence Grounding",
      description: "All market signals and AI insights are strictly grounded in the articles listed below to prevent hallucinations."
    },
    {
      label: "Matched Entity",
      description: "The primary keyword or business entity that triggered the collection and trend detection of the article."
    },
    {
      label: "Quality Status",
      description: "Articles with missing titles or broken links are flagged but retained for volume context. Valid articles have a green check."
    },
    {
      label: "Pagination",
      description: "The dataset displays 5-10 records per page to optimize frontend rendering performance."
    }
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
          <FileText className="h-8 w-8 text-blue-500" />
          Evidence Explorer
        </h1>
        <p className="text-slate-400 mt-2 text-lg">
          What articles support the market signals? Review the foundational data.
        </p>
      </div>

      <MetricExplainer metrics={metrics} />
      
      <div className="animate-in fade-in duration-500 delay-150">
        <ArticlesSection />
      </div>
    </div>
  );
}
