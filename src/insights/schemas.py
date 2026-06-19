from pydantic import BaseModel, Field
from typing import List, Optional

class EvidenceArticle(BaseModel):
    article_id: str
    title: str
    source: str
    keyword: str
    url: str
    published_at: str

class TrendSignalFact(BaseModel):
    keyword: str
    trend_score: float
    confidence_score: float
    article_count: int
    severity: str

class SourceReliabilityFact(BaseModel):
    source: str
    article_count: int
    quality_score: float
    status: str

class InsightCard(BaseModel):
    insight_id: str
    keyword: str
    signal_type: str
    severity: str
    trend_score: float
    confidence_score: float
    article_count: int
    source_count: int
    factual_explanation: str
    business_implication: str
    recommended_next_step: str
    limitation: str
    evidence_articles: List[EvidenceArticle] = []
    generated_by: str = "rule_based"
    created_at: str

class InsightBrief(BaseModel):
    summary: str
    generated_by: str
    insights: List[InsightCard]

class InsightRunSummary(BaseModel):
    run_id: str
    timestamp: str
    status: str
    insights_generated: int
    mode_used: str
    error_message: Optional[str] = None
