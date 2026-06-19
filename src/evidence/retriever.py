from typing import List, Tuple
from datetime import datetime, timezone
from src.evidence.schemas import EvidenceIndex, EvidenceRecord

def compute_relevance_score(record: EvidenceRecord, target_keyword: str) -> Tuple[float, List[str]]:
    """
    Computes a relevance score (0-100 bounds) for an evidence record against a target keyword.
    Returns (score, matched_terms).
    """
    score = 0.0
    matched_terms = []
    
    target_lower = target_keyword.lower()
    
    # 1. Exact keyword match
    if target_lower in record.keyword.lower():
        score += 40.0
        matched_terms.append("exact_keyword")
        
    # 2. Title term match
    if target_lower in record.title.lower():
        score += 25.0
        matched_terms.append("title_match")
        
    # 3. Summary/raw_text match
    if record.summary and target_lower in record.summary.lower():
        score += 15.0
        matched_terms.append("summary_match")
        
    # 4. Source quality (normalized to max +10)
    score += (record.source_quality_score * 10.0)
    
    # 5. Recency (max +10 for within 24h, degrading over time)
    if record.published_at:
        try:
            pub_dt = datetime.fromisoformat(record.published_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            diff_hours = (now - pub_dt).total_seconds() / 3600
            
            if diff_hours < 24:
                score += 10.0
            elif diff_hours < 72:
                score += 5.0
            elif diff_hours < 168: # 1 week
                score += 2.0
        except Exception:
            pass # ignore invalid date formats
            
    # 6. Quality Penalties
    if record.quality_flags:
        flags_lower = record.quality_flags.lower()
        if "missing_url" in flags_lower or "missing_title" in flags_lower:
            score -= 10.0
        if "invalid_url" in flags_lower or "invalid_source" in flags_lower:
            score -= 20.0
            
    # Bounds check
    score = max(0.0, min(100.0, score))
    
    return score, matched_terms

def retrieve_evidence_for_keyword(
    index: EvidenceIndex, 
    keyword: str, 
    top_k: int = 3
) -> List[Tuple[EvidenceRecord, float, List[str]]]:
    """Retrieves top_k evidence records for a given keyword."""
    scored_records = []
    
    for record in index.records:
        score, matched_terms = compute_relevance_score(record, keyword)
        if score > 0 and matched_terms:  # Must have some match to be considered
            scored_records.append((record, score, matched_terms))
            
    # Sort by score descending
    scored_records.sort(key=lambda x: x[1], reverse=True)
    
    return scored_records[:top_k]
