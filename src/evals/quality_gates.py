from src.evals.schemas import QualityGateResult, DataQualityResult, PipelineHealthResult, InsightQualityResult
from typing import List

def evaluate_quality_gates(
    data_quality: DataQualityResult,
    pipeline_health: PipelineHealthResult,
    insight_quality: InsightQualityResult
) -> List[QualityGateResult]:
    
    gates = []
    
    # Pipeline Health Gate
    pipeline_status = "PASS"
    pipeline_reason = "Pipeline is healthy."
    
    if not pipeline_health.required_files_exist:
        pipeline_status = "FAIL"
        pipeline_reason = "Missing required files."
    elif any(c.status == "FAIL" for c in pipeline_health.checks):
        pipeline_status = "FAIL"
        pipeline_reason = "Pipeline checks failed."
    elif any(c.status == "WARN" for c in pipeline_health.checks):
        pipeline_status = "WARN"
        pipeline_reason = "Pipeline has warnings (e.g., stale data)."
        
    gates.append(QualityGateResult(
        gate_name="Pipeline Health Gate",
        status=pipeline_status,
        reason=pipeline_reason
    ))
    
    # Data Quality Gate
    data_status = "PASS"
    data_reason = "Data quality meets expectations."
    
    if data_quality.articles_count == 0 or data_quality.missing_fields_ratio > 0.1:
        data_status = "FAIL"
        data_reason = "No articles found or high missing fields ratio."
    elif data_quality.articles_count < 20 or data_quality.unique_sources < 3:
        data_status = "WARN"
        data_reason = "Low article or source volume."
        
    gates.append(QualityGateResult(
        gate_name="Data Quality Gate",
        status=data_status,
        reason=data_reason
    ))
    
    # Insight Quality Gate
    insight_status = "PASS"
    insight_reason = "Insights meet quality standards."
    
    if insight_quality.banned_phrases_count > 0 or insight_quality.insight_count == 0:
        insight_status = "FAIL"
        insight_reason = "Found banned phrases or zero insights."
    elif insight_quality.insight_count < 3 or insight_quality.completeness_score < 1.0:
        insight_status = "WARN"
        insight_reason = "Low insight count or incomplete insights."
        
    gates.append(QualityGateResult(
        gate_name="Insight Quality Gate",
        status=insight_status,
        reason=insight_reason
    ))
    
    return gates

def compute_overall_status(gates: List[QualityGateResult]) -> str:
    if any(g.status == "FAIL" for g in gates):
        return "FAIL"
    if any(g.status == "WARN" for g in gates):
        return "WARN"
    return "PASS"
