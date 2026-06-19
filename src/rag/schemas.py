from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class RAGQuestion(BaseModel):
    question_id: str
    question: str
    related_keyword: Optional[str] = None
    created_at: str

class RetrievedEvidence(BaseModel):
    citation_id: str
    article_id: str
    title: str
    source: str
    url: str
    keyword: str
    published_at: Optional[str] = None
    relevance_score: float
    matched_terms: List[str]

class RAGAnswer(BaseModel):
    question_id: str
    question: str
    answer: str
    citation_ids: List[str]
    retrieved_evidence: List[RetrievedEvidence]
    generated_by: str  # "rule_based" or "ai_router"
    confidence_note: str
    limitation: str
    created_at: str

class RAGRunManifest(BaseModel):
    run_id: str
    timestamp: str
    questions_processed: int
    answers_generated: int
    ai_answers: int
    rule_based_answers: int
    total_citations_used: int

class RAGRunSummary(BaseModel):
    run_id: str
    timestamp: str
    status: str
    error_message: Optional[str] = None
    manifest: Optional[RAGRunManifest] = None
