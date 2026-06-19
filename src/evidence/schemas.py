from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class EvidenceRecord(BaseModel):
    article_id: str
    title: str
    source: str
    url: str
    keyword: str
    published_at: Optional[str] = None
    summary: Optional[str] = None
    quality_flags: Optional[str] = None
    source_quality_score: float = 0.5

class EvidenceIndex(BaseModel):
    records: List[EvidenceRecord]

class CitationRecord(BaseModel):
    citation_id: str
    article_id: str
    title: str
    source: str
    url: str
    keyword: str
    published_at: Optional[str] = None
    quality_flags: Optional[str] = None
    relevance_score: float
    matched_terms: List[str]
    used_for_insight_id: str

class CitationMap(BaseModel):
    citations: Dict[str, CitationRecord]  # citation_id -> CitationRecord

class InsightEvidenceLink(BaseModel):
    insight_id: str
    keyword: str
    citation_ids: List[str]
    evidence_count: int
    has_evidence: bool
    missing_evidence_reason: Optional[str] = None

class RetrievalManifest(BaseModel):
    run_id: str
    timestamp: str
    articles_indexed: int
    insights_processed: int
    citations_created: int
    insights_missing_evidence: int

class EvidenceRunSummary(BaseModel):
    run_id: str
    timestamp: str
    status: str
    error_message: Optional[str] = None
    manifest: Optional[RetrievalManifest] = None
