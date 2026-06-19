from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CheckResult(BaseModel):
    name: str
    status: str  # "PASS", "WARN", "FAIL"
    score: Optional[float] = None
    message: str
    details: Optional[Dict[str, Any]] = None

class DataQualityResult(BaseModel):
    articles_count: int
    missing_fields_ratio: float
    invalid_keyword_ratio: float
    unique_sources: int
    checks: List[CheckResult]

class PipelineHealthResult(BaseModel):
    required_files_exist: bool
    ingestion_freshness_hours: Optional[float] = None
    analytics_freshness_hours: Optional[float] = None
    pipeline_success_rate: Optional[float] = None
    checks: List[CheckResult]

class InsightQualityResult(BaseModel):
    insight_count: int
    banned_phrases_count: int
    completeness_score: float
    checks: List[CheckResult]

class QualityGateResult(BaseModel):
    gate_name: str
    status: str  # "PASS", "WARN", "FAIL"
    reason: str

class EvaluationSummary(BaseModel):
    run_id: str
    timestamp: str
    overall_status: str  # "PASS", "WARN", "FAIL"
    quality_gates: List[QualityGateResult]
    data_quality: DataQualityResult
    pipeline_health: PipelineHealthResult
    insight_quality: InsightQualityResult

class EvaluationRunSummary(BaseModel):
    run_id: str
    timestamp: str
    status: str
    overall_status: str
    error_message: Optional[str] = None
