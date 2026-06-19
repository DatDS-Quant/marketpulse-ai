import { InsightSection } from "@/components/dashboard/InsightSection";
import { MetricExplainer } from "@/components/dashboard/MetricExplainer";
import { Lightbulb } from "lucide-react";

export default function InsightsPage() {
  const metrics = [
    {
      label: "Deterministic Approach",
      description: "These signals are generated through math and rule-based logic, not speculative LLM prompts."
    },
    {
      label: "Factual Explanation",
      description: "A summary of the metric facts (scores, articles) triggering this insight."
    },
    {
      label: "Limitation",
      description: "Acknowledges potential data gaps, such as low confidence due to a lack of source diversity."
    },
    {
      label: "Practical Next Step",
      description: "A concrete, non-speculative action a human operator should take (e.g., monitor, review evidence)."
    }
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
          <Lightbulb className="h-8 w-8 text-amber-500" />
          Insight Brief
        </h1>
        <p className="text-slate-400 mt-2 text-lg">
          What does the system conclude from the metrics, and what could business users do next?
        </p>
      </div>

      <MetricExplainer metrics={metrics} />
      
      <div className="animate-in fade-in duration-500 delay-150">
        <InsightSection />
      </div>
    </div>
  );
}
