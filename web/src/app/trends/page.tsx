import { TrendSection } from "@/components/dashboard/TrendSection";
import { MetricExplainer } from "@/components/dashboard/MetricExplainer";
import { TrendingUp } from "lucide-react";

export default function TrendsPage() {
  const metrics = [
    {
      label: "Trend Score",
      description: "Signal strength calculated from volume growth and mention velocity over the last 24-48 hours."
    },
    {
      label: "Confidence Score",
      description: "Trust level (0-100) based on data quality, source diversity, and information freshness."
    },
    {
      label: "Articles",
      description: "The total number of collected pieces of evidence mentioning this trend keyword."
    },
    {
      label: "Signal Type",
      description: "Categorization of the trend behavior (e.g. rising_trend, high_volume_stable)."
    }
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
          <TrendingUp className="h-8 w-8 text-blue-500" />
          Trend Intelligence
        </h1>
        <p className="text-slate-400 mt-2 text-lg">
          Which market topics are gaining attention, and how trustworthy are those signals?
        </p>
      </div>

      <MetricExplainer metrics={metrics} />
      
      <TrendSection />
    </div>
  );
}
